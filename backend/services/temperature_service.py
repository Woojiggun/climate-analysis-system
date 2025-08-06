import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import logging
import json

from models.data_models import TemperatureData

logger = logging.getLogger(__name__)

class TemperatureDataService:
    def __init__(self):
        self.nasa_api_key = os.getenv("NASA_API_KEY", "DEMO_KEY")
        self.base_url = "https://climate.nasa.gov/system/internal_resources/details/original"
        self.giss_base_url = "https://data.giss.nasa.gov/gistemp"
        self.cache = {}
        
    def fetch_global_temperature_data(self, start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None) -> List[TemperatureData]:
        """
        Fetch global temperature anomaly data from NASA GISS
        """
        try:
            # Try to fetch from NASA GISS temperature anomaly dataset
            url = f"{self.giss_base_url}/tabledata_v4/GLB.Ts+dSST.csv"
            
            cache_key = f"global_temp_{start_date}_{end_date}"
            if cache_key in self.cache:
                logger.info("Returning cached temperature data")
                return self.cache[cache_key]
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Skip header lines and parse CSV
            lines = response.text.strip().split('\n')
            data_start_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('Year'):
                    data_start_idx = i + 1
                    break
            
            temp_data_list = []
            
            for line in lines[data_start_idx:]:
                parts = line.split(',')
                if len(parts) >= 14:  # Year + 12 months + annual average
                    try:
                        year = int(parts[0])
                        
                        # Process monthly data
                        for month in range(1, 13):
                            temp_anomaly_str = parts[month].strip()
                            if temp_anomaly_str and temp_anomaly_str != '***':
                                temp_anomaly = float(temp_anomaly_str)  # Already in degrees Celsius
                                
                                date = datetime(year, month, 1)
                                
                                # Apply date filters
                                if start_date and date < start_date:
                                    continue
                                if end_date and date > end_date:
                                    continue
                                
                                # Calculate actual temperature (baseline + anomaly)
                                baseline_temp = 14.0  # Global average baseline temperature
                                actual_temp = baseline_temp + temp_anomaly
                                
                                temp_data = TemperatureData(
                                    date=date,
                                    temperature_celsius=actual_temp,
                                    temperature_anomaly=temp_anomaly,
                                    region="Global",
                                    source="NASA GISS"
                                )
                                temp_data_list.append(temp_data)
                                
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Error parsing temperature line: {line}, error: {e}")
                        continue
            
            # Cache the results
            self.cache[cache_key] = temp_data_list
            
            logger.info(f"Successfully fetched {len(temp_data_list)} temperature data points")
            return temp_data_list
            
        except requests.RequestException as e:
            logger.error(f"Error fetching temperature data: {e}")
            return self._get_mock_temperature_data(start_date, end_date)
    
    def fetch_regional_temperature_data(self, region: str, 
                                      start_date: Optional[datetime] = None,
                                      end_date: Optional[datetime] = None) -> List[TemperatureData]:
        """
        Fetch regional temperature data
        """
        # For now, return mock data for regional temperatures
        # In production, this would connect to regional APIs
        return self._get_mock_regional_temperature_data(region, start_date, end_date)
    
    def _get_mock_temperature_data(self, start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None) -> List[TemperatureData]:
        """
        Generate mock temperature data for testing
        """
        if not start_date:
            start_date = datetime(2020, 1, 1)
        if not end_date:
            end_date = datetime.now()
            
        temp_data_list = []
        current_date = start_date
        baseline_temp = 14.0  # Global average baseline
        
        while current_date <= end_date:
            # Simulate warming trend with seasonal variation
            years_elapsed = (current_date.year - 2020)
            warming_trend = years_elapsed * 0.25  # 0.25°C per year (increased warming)
            seasonal_variation = 2.0 * np.sin(2 * np.pi * (current_date.month - 1) / 12)
            
            # Add some random variation
            random_variation = np.random.normal(0, 0.2)
            
            # Calculate temperature with significant warming
            base_anomaly = 1.0 + years_elapsed * 0.15  # Base warming
            temperature_anomaly = base_anomaly + random_variation
            actual_temp = baseline_temp + temperature_anomaly + seasonal_variation
            
            temp_data = TemperatureData(
                date=current_date,
                temperature_celsius=round(actual_temp, 2),
                temperature_anomaly=round(temperature_anomaly, 2),
                region="Global",
                source="NASA GISS (Mock)"
            )
            temp_data_list.append(temp_data)
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
                
        return temp_data_list
    
    def _get_mock_regional_temperature_data(self, region: str,
                                          start_date: Optional[datetime] = None,
                                          end_date: Optional[datetime] = None) -> List[TemperatureData]:
        """
        Generate mock regional temperature data
        """
        if not start_date:
            start_date = datetime(2020, 1, 1)
        if not end_date:
            end_date = datetime.now()
            
        # Regional baseline temperatures
        regional_baselines = {
            "Arctic": -10.0,
            "Europe": 10.0,
            "North America": 12.0,
            "Asia": 14.0,
            "Africa": 22.0,
            "South America": 20.0,
            "Australia": 18.0,
            "Antarctica": -20.0
        }
        
        baseline = regional_baselines.get(region, 15.0)
        
        temp_data_list = []
        current_date = start_date
        
        while current_date <= end_date:
            # Different warming rates for different regions
            warming_multiplier = 2.0 if region == "Arctic" else 1.0
            years_elapsed = (current_date.year - 2020)
            warming_trend = years_elapsed * 0.15 * warming_multiplier
            
            seasonal_variation = 3.0 * np.sin(2 * np.pi * (current_date.month - 1) / 12)
            if region in ["Arctic", "Antarctica"]:
                seasonal_variation *= 3  # More extreme seasonal variation in polar regions
                
            temperature_anomaly = warming_trend + np.random.normal(0, 0.3)
            actual_temp = baseline + temperature_anomaly + seasonal_variation
            
            temp_data = TemperatureData(
                date=current_date,
                temperature_celsius=round(actual_temp, 2),
                temperature_anomaly=round(temperature_anomaly, 2),
                region=region,
                source="Regional Climate Model (Mock)"
            )
            temp_data_list.append(temp_data)
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
                
        return temp_data_list