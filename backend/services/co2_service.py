import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional
import logging
from io import StringIO

from models.data_models import CO2Data

logger = logging.getLogger(__name__)

class CO2DataService:
    def __init__(self):
        self.noaa_api_key = os.getenv("NOAA_API_KEY", "")
        self.base_url = "https://gml.noaa.gov/webdata/ccgg/trends/co2"
        self.cache = {}
        
    def fetch_monthly_co2_data(self, start_date: Optional[datetime] = None, 
                              end_date: Optional[datetime] = None) -> List[CO2Data]:
        """
        Fetch monthly CO2 data from NOAA Mauna Loa observatory
        """
        try:
            # NOAA provides public CO2 data without API key requirement
            url = f"{self.base_url}/co2_mm_mlo.txt"
            
            # Check cache first
            cache_key = f"monthly_co2_{start_date}_{end_date}"
            if cache_key in self.cache:
                logger.info("Returning cached CO2 data")
                return self.cache[cache_key]
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse the text data
            lines = response.text.strip().split('\n')
            data_lines = [line for line in lines if line and not line.startswith('#')]
            
            co2_data_list = []
            for line in data_lines:
                parts = line.split()
                if len(parts) >= 5:
                    try:
                        year = int(parts[0])
                        month = int(parts[1])
                        decimal_date = float(parts[2])
                        average_ppm = float(parts[3])
                        
                        # Skip invalid measurements
                        if average_ppm < 0:
                            continue
                            
                        date = datetime(year, month, 1)
                        
                        # Apply date filters if provided
                        if start_date and date < start_date:
                            continue
                        if end_date and date > end_date:
                            continue
                            
                        co2_data = CO2Data(
                            date=date,
                            ppm=average_ppm,
                            location="Mauna Loa",
                            source="NOAA"
                        )
                        co2_data_list.append(co2_data)
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Error parsing line: {line}, error: {e}")
                        continue
            
            # Cache the results
            self.cache[cache_key] = co2_data_list
            
            logger.info(f"Successfully fetched {len(co2_data_list)} CO2 data points")
            if co2_data_list:
                logger.info(f"Data range: {co2_data_list[0].date} to {co2_data_list[-1].date}")
            return co2_data_list
            
        except requests.RequestException as e:
            logger.error(f"Error fetching CO2 data: {e}")
            # Return mock data for testing if API fails
            logger.info("Using mock CO2 data due to API error")
            return self._get_mock_co2_data(start_date, end_date)
    
    def fetch_daily_co2_data(self, days: int = 365) -> List[CO2Data]:
        """
        Fetch daily CO2 data for the specified number of days
        """
        try:
            url = f"{self.base_url}/co2_daily_mlo.txt"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            lines = response.text.strip().split('\n')
            data_lines = [line for line in lines if line and not line.startswith('#')]
            
            co2_data_list = []
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            for line in data_lines:
                parts = line.split()
                if len(parts) >= 5:
                    try:
                        year = int(parts[0])
                        month = int(parts[1])
                        day = int(parts[2])
                        average_ppm = float(parts[4])
                        
                        if average_ppm < 0:
                            continue
                            
                        date = datetime(year, month, day)
                        
                        if date < start_date or date > end_date:
                            continue
                            
                        co2_data = CO2Data(
                            date=date,
                            ppm=average_ppm,
                            location="Mauna Loa",
                            source="NOAA"
                        )
                        co2_data_list.append(co2_data)
                    except (ValueError, IndexError) as e:
                        continue
            
            return co2_data_list
            
        except requests.RequestException as e:
            logger.error(f"Error fetching daily CO2 data: {e}")
            return []
    
    def _get_mock_co2_data(self, start_date: Optional[datetime] = None, 
                          end_date: Optional[datetime] = None) -> List[CO2Data]:
        """
        Generate mock CO2 data for testing
        """
        if not start_date:
            start_date = datetime(2020, 1, 1)
        if not end_date:
            end_date = datetime.now()
            
        co2_data_list = []
        current_date = start_date
        base_ppm = 410.0
        
        while current_date <= end_date:
            # Simulate seasonal variation and upward trend
            months_elapsed = (current_date.year - 2020) * 12 + current_date.month
            trend = months_elapsed * 0.2  # 0.2 ppm per month increase
            seasonal = 3.0 * np.sin(2 * np.pi * current_date.month / 12)
            
            ppm = base_ppm + trend + seasonal
            
            co2_data = CO2Data(
                date=current_date,
                ppm=round(ppm, 2),
                location="Mauna Loa",
                source="NOAA (Mock)"
            )
            co2_data_list.append(co2_data)
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
                
        return co2_data_list