from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class CO2Data(BaseModel):
    date: datetime
    ppm: float = Field(..., description="CO2 concentration in parts per million")
    location: str = Field(default="Mauna Loa", description="Measurement location")
    source: str = Field(default="NOAA", description="Data source")
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-01-01T00:00:00",
                "ppm": 421.78,
                "location": "Mauna Loa",
                "source": "NOAA"
            }
        }

class TemperatureData(BaseModel):
    date: datetime
    temperature_celsius: float = Field(..., description="Temperature in Celsius")
    temperature_anomaly: Optional[float] = Field(None, description="Temperature anomaly from baseline")
    region: str = Field(..., description="Geographic region")
    source: str = Field(default="NASA GISS", description="Data source")
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-01-01T00:00:00",
                "temperature_celsius": 15.5,
                "temperature_anomaly": 1.2,
                "region": "Global",
                "source": "NASA GISS"
            }
        }

class GroundwaterData(BaseModel):
    date: datetime
    water_level_m: float = Field(..., description="Water level in meters")
    change_from_baseline: Optional[float] = Field(None, description="Change from baseline in meters")
    location: str = Field(..., description="Well or region location")
    source: str = Field(default="USGS", description="Data source")
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-01-01T00:00:00",
                "water_level_m": -2.5,
                "change_from_baseline": -0.3,
                "location": "California Central Valley",
                "source": "USGS"
            }
        }

class CO2GapAnalysis(BaseModel):
    date: datetime
    co2_ppm: float
    theoretical_temp: float = Field(..., description="Theoretical temperature based on CO2")
    actual_temp: float = Field(..., description="Actual measured temperature")
    unexplained_gap: float = Field(..., description="Temperature gap not explained by CO2")
    gap_percentage: float = Field(..., description="Gap as percentage of theoretical temp")
    p_value: float = Field(..., description="Statistical significance p-value")
    confidence_interval: tuple[float, float] = Field(..., description="95% confidence interval")
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-01-01T00:00:00",
                "co2_ppm": 421.78,
                "theoretical_temp": 1.5,
                "actual_temp": 2.1,
                "unexplained_gap": 0.6,
                "gap_percentage": 40.0,
                "p_value": 0.001,
                "confidence_interval": [0.4, 0.8]
            }
        }