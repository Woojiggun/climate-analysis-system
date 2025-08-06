from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
from typing import List, Optional
import logging

from models.data_models import TemperatureData
from services.temperature_service import TemperatureDataService

router = APIRouter()
logger = logging.getLogger(__name__)
temperature_service = TemperatureDataService()

@router.get("/global", response_model=List[TemperatureData])
async def get_global_temperature_data(
    start_date: Optional[datetime] = Query(None, description="Start date for data retrieval"),
    end_date: Optional[datetime] = Query(None, description="End date for data retrieval")
):
    """
    Get global temperature data including anomalies from NASA GISS
    """
    try:
        data = temperature_service.fetch_global_temperature_data(start_date, end_date)
        if not data:
            raise HTTPException(status_code=404, detail="No temperature data found for the specified period")
        return data
    except Exception as e:
        logger.error(f"Error retrieving global temperature data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/regional/{region}", response_model=List[TemperatureData])
async def get_regional_temperature_data(
    region: str,
    start_date: Optional[datetime] = Query(None, description="Start date for data retrieval"),
    end_date: Optional[datetime] = Query(None, description="End date for data retrieval")
):
    """
    Get temperature data for a specific region
    
    Available regions: Arctic, Europe, North America, Asia, Africa, South America, Australia, Antarctica
    """
    valid_regions = ["Arctic", "Europe", "North America", "Asia", "Africa", 
                     "South America", "Australia", "Antarctica"]
    
    if region not in valid_regions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid region. Choose from: {', '.join(valid_regions)}"
        )
    
    try:
        data = temperature_service.fetch_regional_temperature_data(region, start_date, end_date)
        if not data:
            raise HTTPException(status_code=404, detail=f"No temperature data found for {region}")
        return data
    except Exception as e:
        logger.error(f"Error retrieving regional temperature data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest", response_model=TemperatureData)
async def get_latest_temperature_data(
    region: str = Query("Global", description="Region for temperature data")
):
    """
    Get the most recent temperature measurement for a region
    """
    try:
        if region == "Global":
            data = temperature_service.fetch_global_temperature_data()
        else:
            data = temperature_service.fetch_regional_temperature_data(region)
            
        if not data:
            raise HTTPException(status_code=404, detail="No temperature data available")
        return max(data, key=lambda x: x.date)
    except Exception as e:
        logger.error(f"Error retrieving latest temperature data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_temperature_summary(
    region: str = Query("Global", description="Region for temperature summary"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """
    Get summary statistics for temperature data
    """
    try:
        if region == "Global":
            data = temperature_service.fetch_global_temperature_data(start_date, end_date)
        else:
            data = temperature_service.fetch_regional_temperature_data(region, start_date, end_date)
            
        if not data:
            raise HTTPException(status_code=404, detail="No temperature data found for summary")
        
        temps = [d.temperature_celsius for d in data]
        anomalies = [d.temperature_anomaly for d in data if d.temperature_anomaly is not None]
        
        return {
            "region": region,
            "period": {
                "start": min(d.date for d in data).isoformat(),
                "end": max(d.date for d in data).isoformat()
            },
            "temperature_statistics": {
                "mean_celsius": sum(temps) / len(temps),
                "min_celsius": min(temps),
                "max_celsius": max(temps),
                "latest_celsius": data[-1].temperature_celsius,
                "data_points": len(data)
            },
            "anomaly_statistics": {
                "mean_anomaly": sum(anomalies) / len(anomalies) if anomalies else 0,
                "max_anomaly": max(anomalies) if anomalies else 0,
                "min_anomaly": min(anomalies) if anomalies else 0,
                "latest_anomaly": data[-1].temperature_anomaly if data[-1].temperature_anomaly else 0
            },
            "warming_trend": {
                "total_warming": data[-1].temperature_celsius - data[0].temperature_celsius if len(data) > 1 else 0,
                "rate_per_year": ((data[-1].temperature_celsius - data[0].temperature_celsius) / 
                                 ((data[-1].date - data[0].date).days / 365.25)) if len(data) > 1 else 0
            }
        }
    except Exception as e:
        logger.error(f"Error generating temperature summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compare")
async def compare_temperature_trends(
    regions: List[str] = Query(..., description="List of regions to compare"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """
    Compare temperature trends across multiple regions
    """
    try:
        comparison_data = {}
        
        for region in regions:
            if region == "Global":
                data = temperature_service.fetch_global_temperature_data(start_date, end_date)
            else:
                data = temperature_service.fetch_regional_temperature_data(region, start_date, end_date)
                
            if data:
                temps = [d.temperature_celsius for d in data]
                comparison_data[region] = {
                    "mean_temperature": sum(temps) / len(temps),
                    "warming_rate": ((data[-1].temperature_celsius - data[0].temperature_celsius) / 
                                   ((data[-1].date - data[0].date).days / 365.25)) if len(data) > 1 else 0,
                    "max_temperature": max(temps),
                    "min_temperature": min(temps),
                    "data_points": len(data)
                }
        
        return {
            "comparison": comparison_data,
            "period": {
                "start": start_date.isoformat() if start_date else "earliest available",
                "end": end_date.isoformat() if end_date else "latest available"
            }
        }
    except Exception as e:
        logger.error(f"Error comparing temperature trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))