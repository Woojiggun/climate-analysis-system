from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
from typing import List, Optional
import logging

from models.data_models import CO2Data
from services.co2_service import CO2DataService

router = APIRouter()
logger = logging.getLogger(__name__)
co2_service = CO2DataService()

@router.get("/monthly", response_model=List[CO2Data])
async def get_monthly_co2_data(
    start_date: Optional[datetime] = Query(None, description="Start date for data retrieval"),
    end_date: Optional[datetime] = Query(None, description="End date for data retrieval")
):
    """
    Get monthly CO2 concentration data from NOAA
    """
    try:
        data = co2_service.fetch_monthly_co2_data(start_date, end_date)
        if not data:
            raise HTTPException(status_code=404, detail="No CO2 data found for the specified period")
        return data
    except Exception as e:
        logger.error(f"Error retrieving monthly CO2 data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/daily", response_model=List[CO2Data])
async def get_daily_co2_data(
    days: int = Query(365, ge=1, le=3650, description="Number of days of data to retrieve")
):
    """
    Get daily CO2 concentration data for the specified number of days
    """
    try:
        data = co2_service.fetch_daily_co2_data(days)
        if not data:
            raise HTTPException(status_code=404, detail="No daily CO2 data found")
        return data
    except Exception as e:
        logger.error(f"Error retrieving daily CO2 data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest", response_model=CO2Data)
async def get_latest_co2_data():
    """
    Get the most recent CO2 concentration measurement
    """
    try:
        data = co2_service.fetch_monthly_co2_data()
        if not data:
            raise HTTPException(status_code=404, detail="No CO2 data available")
        # Return the most recent data point
        return max(data, key=lambda x: x.date)
    except Exception as e:
        logger.error(f"Error retrieving latest CO2 data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_co2_summary(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """
    Get summary statistics for CO2 data
    """
    try:
        data = co2_service.fetch_monthly_co2_data(start_date, end_date)
        if not data:
            raise HTTPException(status_code=404, detail="No CO2 data found for summary")
        
        ppm_values = [d.ppm for d in data]
        
        return {
            "period": {
                "start": min(d.date for d in data).isoformat(),
                "end": max(d.date for d in data).isoformat()
            },
            "statistics": {
                "mean_ppm": sum(ppm_values) / len(ppm_values),
                "min_ppm": min(ppm_values),
                "max_ppm": max(ppm_values),
                "latest_ppm": data[-1].ppm,
                "total_increase": data[-1].ppm - data[0].ppm,
                "data_points": len(data)
            },
            "trend": {
                "monthly_average_increase": (data[-1].ppm - data[0].ppm) / len(data) if len(data) > 1 else 0,
                "annual_average_increase": ((data[-1].ppm - data[0].ppm) / len(data)) * 12 if len(data) > 1 else 0
            }
        }
    except Exception as e:
        logger.error(f"Error generating CO2 summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))