from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
from typing import List, Optional
import logging

from models.data_models import GroundwaterData
from services.groundwater_service import GroundwaterDataService

router = APIRouter()
logger = logging.getLogger(__name__)
groundwater_service = GroundwaterDataService()

@router.get("/data", response_model=List[GroundwaterData])
async def get_groundwater_data(
    location: str = Query("California Central Valley", description="Location/aquifer name"),
    start_date: Optional[datetime] = Query(None, description="Start date for data retrieval"),
    end_date: Optional[datetime] = Query(None, description="End date for data retrieval")
):
    """
    Get groundwater level data for a specific location
    
    Available locations:
    - California Central Valley
    - Ogallala Aquifer
    - North China Plain
    - Indo-Gangetic Basin
    - Arabian Aquifer
    - Global Average
    """
    try:
        data = groundwater_service.fetch_groundwater_data(location, start_date, end_date)
        if not data:
            raise HTTPException(status_code=404, detail=f"No groundwater data found for {location}")
        return data
    except Exception as e:
        logger.error(f"Error retrieving groundwater data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/locations")
async def get_available_locations():
    """
    Get list of available groundwater monitoring locations
    """
    return {
        "locations": [
            {
                "name": "California Central Valley",
                "region": "North America",
                "severity": "severe",
                "depletion_rate": -0.5
            },
            {
                "name": "Ogallala Aquifer",
                "region": "North America",
                "severity": "moderate",
                "depletion_rate": -0.3
            },
            {
                "name": "North China Plain",
                "region": "Asia",
                "severity": "critical",
                "depletion_rate": -0.8
            },
            {
                "name": "Indo-Gangetic Basin",
                "region": "Asia",
                "severity": "severe",
                "depletion_rate": -0.6
            },
            {
                "name": "Arabian Aquifer",
                "region": "Middle East",
                "severity": "extreme",
                "depletion_rate": -1.0
            },
            {
                "name": "Global Average",
                "region": "Worldwide",
                "severity": "moderate",
                "depletion_rate": -0.2
            }
        ]
    }

@router.get("/summary")
async def get_groundwater_summary(
    location: str = Query("California Central Valley"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """
    Get summary statistics for groundwater data
    """
    try:
        data = groundwater_service.fetch_groundwater_data(location, start_date, end_date)
        
        if not data:
            raise HTTPException(status_code=404, detail="No groundwater data found for summary")
        
        levels = [d.water_level_m for d in data]
        changes = [d.change_from_baseline for d in data]
        
        return {
            "location": location,
            "data_source": data[0].source if data else "Unknown",
            "period": {
                "start": min(d.date for d in data).isoformat(),
                "end": max(d.date for d in data).isoformat()
            },
            "statistics": {
                "mean_level": sum(levels) / len(levels),
                "latest_level": data[-1].water_level_m,
                "lowest_level": min(levels),
                "highest_level": max(levels),
                "data_points": len(data)
            },
            "depletion": {
                "total_depletion": data[-1].water_level_m - data[0].water_level_m,
                "annual_rate": ((data[-1].water_level_m - data[0].water_level_m) / 
                                ((data[-1].date - data[0].date).days / 365.25)),
                "cumulative_change": data[-1].change_from_baseline
            },
            "trend": "depleting" if data[-1].water_level_m < data[0].water_level_m else "recovering"
        }
    except Exception as e:
        logger.error(f"Error generating groundwater summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/regional-comparison")
async def compare_regional_groundwater(
    regions: List[str] = Query(..., description="List of regions to compare"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """
    Compare groundwater depletion across multiple regions
    """
    try:
        comparison = groundwater_service.get_regional_summary(regions, start_date, end_date)
        
        return {
            "comparison": comparison,
            "period": {
                "start": start_date.isoformat() if start_date else "earliest available",
                "end": end_date.isoformat() if end_date else "latest available"
            },
            "most_depleted": min(comparison.items(), 
                               key=lambda x: x[1]["depletion_rate"])[0] if comparison else None,
            "fastest_depletion": min(comparison.items(), 
                                   key=lambda x: x[1]["depletion_rate"])[0] if comparison else None
        }
    except Exception as e:
        logger.error(f"Error comparing regional groundwater: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/correlation-data")
async def get_correlation_ready_data(
    location: str = Query("California Central Valley"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """
    Get groundwater data formatted for correlation analysis with temperature
    """
    try:
        data = groundwater_service.fetch_groundwater_data(location, start_date, end_date)
        
        if not data:
            raise HTTPException(status_code=404, detail="No groundwater data found")
        
        # Format data for correlation analysis
        return {
            "location": location,
            "dates": [d.date.isoformat() for d in data],
            "water_levels": [d.water_level_m for d in data],
            "changes": [d.change_from_baseline for d in data],
            "metadata": {
                "unit": "meters below surface",
                "source": data[0].source if data else "Unknown",
                "data_points": len(data)
            }
        }
    except Exception as e:
        logger.error(f"Error preparing correlation data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usgs/sites")
async def get_usgs_monitoring_sites(
    state_code: str = Query("CA", description="US state code"),
    site_type: str = Query("GW", description="Site type (GW for groundwater)"),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get USGS groundwater monitoring sites for future integration.
    This endpoint is prepared for USGS API integration.
    """
    # Placeholder for USGS site data
    # In production, this would query: https://waterservices.usgs.gov/nwis/site/
    return {
        "state": state_code,
        "site_type": site_type,
        "sites": [
            {
                "site_id": "373829122075801",
                "site_name": "California Central Valley Well 1",
                "latitude": 37.6414,
                "longitude": -122.1328,
                "aquifer": "Central Valley Aquifer System",
                "status": "active"
            },
            {
                "site_id": "364200119440401", 
                "site_name": "San Joaquin Valley Monitoring Well",
                "latitude": 36.7000,
                "longitude": -119.7339,
                "aquifer": "San Joaquin Valley",
                "status": "active"
            }
        ],
        "total_sites": 2,
        "api_ready": False,
        "integration_note": "USGS API integration pending"
    }

@router.get("/usgs/data/{site_id}")
async def get_usgs_site_data(
    site_id: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    parameter_code: str = Query("72019", description="USGS parameter code (72019 for groundwater level)")
):
    """
    Get groundwater data from USGS for a specific site.
    Prepared for future USGS NWIS API integration.
    """
    # Placeholder response structure matching USGS API format
    # In production: https://waterservices.usgs.gov/nwis/gwlevels/
    return {
        "site_id": site_id,
        "parameter": {
            "code": parameter_code,
            "name": "Depth to water level, feet below land surface"
        },
        "data": [
            {
                "datetime": "2024-01-15T12:00:00",
                "value": 125.5,
                "unit": "ft",
                "quality_code": "A"
            },
            {
                "datetime": "2024-02-15T12:00:00", 
                "value": 126.2,
                "unit": "ft",
                "quality_code": "A"
            }
        ],
        "api_ready": False,
        "integration_note": "Real-time USGS data pending API key and implementation"
    }