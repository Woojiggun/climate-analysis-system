import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import logging
import json

from models.data_models import GroundwaterData

logger = logging.getLogger(__name__)

class GroundwaterDataService:
    def __init__(self):
        self.usgs_api_key = os.getenv("USGS_API_KEY", "")
        self.base_url = "https://waterservices.usgs.gov/nwis"
        self.cache = {}
        
    def fetch_groundwater_data(self, location: str = "California Central Valley",
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> List[GroundwaterData]:
        """
        Fetch groundwater level data from USGS or return mock data
        """
        try:
            cache_key = f"groundwater_{location}_{start_date}_{end_date}"
            if cache_key in self.cache:
                logger.info("Returning cached groundwater data")
                return self.cache[cache_key]
            
            # Try to fetch real USGS data
            data = self._fetch_usgs_groundwater_data(location, start_date, end_date)
            
            if not data:
                logger.info(f"No USGS data available for {location}, using mock data")
                data = self._generate_mock_groundwater_data(location, start_date, end_date)
            
            # Cache the results
            self.cache[cache_key] = data
            
            logger.info(f"Retrieved {len(data)} groundwater data points for {location}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching groundwater data: {e}")
            return self._generate_mock_groundwater_data(location, start_date, end_date)
    
    def _generate_mock_groundwater_data(self, location: str,
                                      start_date: Optional[datetime] = None,
                                      end_date: Optional[datetime] = None) -> List[GroundwaterData]:
        """
        Generate realistic mock groundwater depletion data
        """
        if start_date is None:
            start_date = datetime(2020, 1, 1)
        if end_date is None:
            end_date = datetime.now()
            
        groundwater_data_list = []
        current_date = start_date
        
        # Regional baseline water levels (meters below surface)
        regional_baselines = {
            "California Central Valley": -30.0,  # Severe depletion
            "Ogallala Aquifer": -25.0,          # High Plains aquifer
            "North China Plain": -35.0,          # Critical depletion
            "Indo-Gangetic Basin": -28.0,       # India/Pakistan
            "Arabian Aquifer": -40.0,            # Middle East
            "Global Average": -20.0              # World average
        }
        
        baseline = regional_baselines.get(location, -20.0)
        
        # Depletion rates (meters per year)
        depletion_rates = {
            "California Central Valley": -0.5,   # 0.5m/year depletion
            "Ogallala Aquifer": -0.3,
            "North China Plain": -0.8,          # Severe depletion
            "Indo-Gangetic Basin": -0.6,
            "Arabian Aquifer": -1.0,            # Extreme depletion
            "Global Average": -0.2
        }
        
        depletion_rate = depletion_rates.get(location, -0.2)
        
        while current_date <= end_date:
            # Calculate years elapsed
            years_elapsed = (current_date - start_date).days / 365.25
            
            # Progressive depletion with seasonal variation
            trend_depletion = years_elapsed * depletion_rate
            
            # Seasonal variation (wet/dry seasons)
            # Winter/spring (months 1-3, 12) should have higher levels, summer (months 6-9) lower
            seasonal_variation = -2.0 * np.sin(2 * np.pi * (current_date.month - 3) / 12)
            
            # Random variation
            random_variation = np.random.normal(0, 0.5)
            
            # Calculate water level
            water_level = baseline + trend_depletion + seasonal_variation + random_variation
            
            # Calculate change from baseline
            change_from_baseline = water_level - baseline
            
            groundwater_data = GroundwaterData(
                date=current_date,
                water_level_m=round(water_level, 2),
                change_from_baseline=round(change_from_baseline, 2),
                location=location,
                source="USGS (Mock)"
            )
            groundwater_data_list.append(groundwater_data)
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
                
        return groundwater_data_list
    
    def _fetch_usgs_groundwater_data(self, location: str,
                                     start_date: Optional[datetime] = None,
                                     end_date: Optional[datetime] = None) -> List[GroundwaterData]:
        """
        Fetch real groundwater data from USGS Water Services API
        """
        # Map location names to USGS site codes
        # These are example site codes for groundwater monitoring wells
        site_mapping = {
            "California Central Valley": "373030119270801,365632120060801,364818119445001",  # CA wells
            "Ogallala Aquifer": "341737101144001,355800100303401",  # High Plains wells
            "Global Average": "373030119270801"  # Default to CA well
        }
        
        site_codes = site_mapping.get(location, site_mapping["Global Average"])
        
        try:
            # Format dates for USGS API
            if start_date:
                start_str = start_date.strftime("%Y-%m-%d")
            else:
                start_str = (datetime.now() - timedelta(days=365*5)).strftime("%Y-%m-%d")
                
            if end_date:
                end_str = end_date.strftime("%Y-%m-%d")
            else:
                end_str = datetime.now().strftime("%Y-%m-%d")
            
            # USGS API parameters
            params = {
                "sites": site_codes,
                "startDT": start_str,
                "endDT": end_str,
                "parameterCd": "72019",  # Depth to water level, feet below land surface
                "siteStatus": "all",
                "format": "json"
            }
            
            url = f"{self.base_url}/dv/"
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            groundwater_data_list = []
            
            if "value" in data and "timeSeries" in data["value"]:
                for site_data in data["value"]["timeSeries"]:
                    site_name = site_data.get("sourceInfo", {}).get("siteName", location)
                    
                    if "values" in site_data and site_data["values"]:
                        for value_set in site_data["values"]:
                            if "value" in value_set:
                                baseline_level = None
                                
                                for value_point in value_set["value"]:
                                    try:
                                        date_str = value_point["dateTime"]
                                        date = datetime.fromisoformat(date_str.replace("T", " ").split(".")[0])
                                        
                                        # Convert feet to meters (negative because it's depth below surface)
                                        depth_feet = float(value_point["value"])
                                        depth_meters = -depth_feet * 0.3048
                                        
                                        if baseline_level is None:
                                            baseline_level = depth_meters
                                        
                                        change_from_baseline = depth_meters - baseline_level
                                        
                                        groundwater_data = GroundwaterData(
                                            date=date,
                                            water_level_m=round(depth_meters, 2),
                                            change_from_baseline=round(change_from_baseline, 2),
                                            location=location,
                                            source="USGS"
                                        )
                                        groundwater_data_list.append(groundwater_data)
                                        
                                    except (ValueError, KeyError) as e:
                                        logger.warning(f"Error parsing USGS value: {e}")
                                        continue
            
            # Aggregate monthly if we have daily data
            if groundwater_data_list and len(groundwater_data_list) > 100:
                # Group by month and average
                monthly_data = {}
                for data_point in groundwater_data_list:
                    month_key = data_point.date.strftime("%Y-%m")
                    if month_key not in monthly_data:
                        monthly_data[month_key] = []
                    monthly_data[month_key].append(data_point)
                
                aggregated_data = []
                for month_key, month_points in sorted(monthly_data.items()):
                    avg_level = sum(p.water_level_m for p in month_points) / len(month_points)
                    avg_change = sum(p.change_from_baseline for p in month_points) / len(month_points)
                    
                    # Use first day of month for date
                    date = datetime.strptime(month_key + "-01", "%Y-%m-%d")
                    
                    groundwater_data = GroundwaterData(
                        date=date,
                        water_level_m=round(avg_level, 2),
                        change_from_baseline=round(avg_change, 2),
                        location=location,
                        source="USGS"
                    )
                    aggregated_data.append(groundwater_data)
                
                groundwater_data_list = aggregated_data
            
            logger.info(f"Successfully fetched {len(groundwater_data_list)} USGS groundwater data points")
            return groundwater_data_list
            
        except Exception as e:
            logger.error(f"Error fetching USGS data: {e}")
            return []
    
    def get_regional_summary(self, regions: List[str],
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> Dict:
        """
        Get summary statistics for multiple regions
        """
        summary = {}
        
        for region in regions:
            data = self.fetch_groundwater_data(region, start_date, end_date)
            
            if data:
                levels = [d.water_level_m for d in data]
                changes = [d.change_from_baseline for d in data]
                
                summary[region] = {
                    "average_level": sum(levels) / len(levels),
                    "total_depletion": data[-1].water_level_m - data[0].water_level_m,
                    "depletion_rate": (data[-1].water_level_m - data[0].water_level_m) / 
                                     ((data[-1].date - data[0].date).days / 365.25),
                    "latest_level": data[-1].water_level_m,
                    "data_points": len(data)
                }
        
        return summary