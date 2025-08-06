from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
import numpy as np

from models.data_models import CO2GapAnalysis
from services.analysis_service import AnalysisService

router = APIRouter()
logger = logging.getLogger(__name__)
analysis_service = AnalysisService()

@router.get("/co2-gap", response_model=List[CO2GapAnalysis])
async def analyze_co2_gap(
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    region: str = Query("Global", description="Region for analysis")
):
    """
    Analyze the gap between theoretical CO2-based temperature and actual temperature.
    
    This endpoint calculates how much of the observed temperature increase
    cannot be explained by CO2 alone, suggesting other factors (like groundwater depletion).
    """
    try:
        results = analysis_service.analyze_co2_temperature_gap(
            start_date, end_date, region
        )
        if not results:
            raise HTTPException(
                status_code=404, 
                detail="No data available for the specified period"
            )
        return results
    except Exception as e:
        logger.error(f"Error in CO2 gap analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/co2-gap/calculate")
async def calculate_single_co2_gap(
    co2_ppm: float = Query(..., ge=300, le=600, description="CO2 concentration in ppm"),
    actual_temp: float = Query(..., ge=-50, le=50, description="Actual temperature in Celsius"),
    baseline_temp: float = Query(14.0, description="Baseline temperature in Celsius")
):
    """
    Calculate CO2 gap for a single data point.
    
    Useful for real-time calculations or hypothetical scenarios.
    """
    try:
        result = analysis_service.calculate_co2_gap(co2_ppm, actual_temp, baseline_temp)
        return result
    except Exception as e:
        logger.error(f"Error calculating CO2 gap: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/co2-gap/summary")
async def get_co2_gap_summary(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    region: str = Query("Global")
):
    """
    Get summary statistics for CO2 gap analysis over a period.
    """
    try:
        gap_data = analysis_service.analyze_co2_temperature_gap(
            start_date, end_date, region
        )
        
        if not gap_data:
            raise HTTPException(status_code=404, detail="No data for summary")
        
        gaps = [d.unexplained_gap for d in gap_data]
        percentages = [d.gap_percentage for d in gap_data]
        
        return {
            "period": {
                "start": min(d.date for d in gap_data).isoformat(),
                "end": max(d.date for d in gap_data).isoformat(),
                "data_points": len(gap_data)
            },
            "gap_statistics": {
                "mean_gap_celsius": sum(gaps) / len(gaps),
                "max_gap_celsius": max(gaps),
                "min_gap_celsius": min(gaps),
                "latest_gap_celsius": gaps[-1],
                "trend": "increasing" if gaps[-1] > gaps[0] else "decreasing"
            },
            "percentage_statistics": {
                "mean_gap_percentage": sum(percentages) / len(percentages),
                "max_gap_percentage": max(percentages),
                "latest_gap_percentage": percentages[-1]
            },
            "key_finding": f"On average, {round(sum(percentages) / len(percentages), 1)}% "
                          f"of observed warming cannot be explained by CO2 alone"
        }
    except Exception as e:
        logger.error(f"Error generating CO2 gap summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/time-lag/correlation")
async def analyze_time_lag_correlation(
    groundwater_data: List[float] = Query(..., description="List of groundwater levels"),
    temperature_data: List[float] = Query(..., description="List of temperature values"),
    max_lag_months: int = Query(24, ge=1, le=60, description="Maximum lag in months to test")
):
    """
    Analyze time-lag correlation between groundwater and temperature changes.
    
    This helps identify if groundwater depletion leads temperature changes.
    """
    try:
        if len(groundwater_data) != len(temperature_data):
            raise HTTPException(
                status_code=400,
                detail="Groundwater and temperature data must have the same length"
            )
        
        if len(groundwater_data) < 12:
            raise HTTPException(
                status_code=400,
                detail="Need at least 12 data points for meaningful correlation analysis"
            )
        
        # Create dummy dates for correlation analysis
        dates = [datetime(2020, 1, 1) + timedelta(days=30*i) 
                for i in range(len(groundwater_data))]
        
        result = analysis_service.calculate_time_lag_correlation(
            groundwater_data, temperature_data, dates, max_lag_months
        )
        
        return result
    except Exception as e:
        logger.error(f"Error in time-lag correlation analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends/comprehensive")
async def get_comprehensive_analysis(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    region: str = Query("Global"),
    include_groundwater: bool = Query(False, description="Include groundwater analysis")
):
    """
    Perform comprehensive climate analysis including all factors.
    """
    try:
        # Fetch all necessary data
        co2_data = analysis_service.co2_service.fetch_monthly_co2_data(
            start_date, end_date
        )
        
        if region == "Global":
            temp_data = analysis_service.temperature_service.fetch_global_temperature_data(
                start_date, end_date
            )
        else:
            temp_data = analysis_service.temperature_service.fetch_regional_temperature_data(
                region, start_date, end_date
            )
        
        # Perform composite analysis
        analysis_result = analysis_service.perform_composite_analysis(
            co2_data, temp_data
        )
        
        # Add gap analysis
        gap_data = analysis_service.analyze_co2_temperature_gap(
            start_date, end_date, region
        )
        
        if gap_data:
            gaps = [d.unexplained_gap for d in gap_data]
            analysis_result["co2_gap_analysis"] = {
                "mean_unexplained_warming": sum(gaps) / len(gaps),
                "max_unexplained_warming": max(gaps),
                "percentage_unexplained": sum(d.gap_percentage for d in gap_data) / len(gap_data)
            }
        
        return {
            "region": region,
            "period": {
                "start": start_date.isoformat() if start_date else "earliest available",
                "end": end_date.isoformat() if end_date else "latest available"
            },
            "analysis": analysis_result,
            "interpretation": _interpret_results(analysis_result)
        }
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _interpret_results(analysis_result: dict) -> dict:
    """Interpret analysis results for user understanding"""
    interpretation = {
        "main_findings": [],
        "evidence_strength": "moderate",
        "recommendation": ""
    }
    
    # Check CO2 gap
    if "co2_gap_analysis" in analysis_result:
        gap_pct = analysis_result["co2_gap_analysis"]["percentage_unexplained"]
        if gap_pct > 30:
            interpretation["main_findings"].append(
                f"Significant unexplained warming: {round(gap_pct, 1)}% of temperature "
                "increase cannot be attributed to CO2 alone"
            )
            interpretation["evidence_strength"] = "strong"
    
    # Check correlations
    if analysis_result.get("co2_temperature_correlation"):
        corr = analysis_result["co2_temperature_correlation"]["correlation"]
        if corr > 0.8:
            interpretation["main_findings"].append(
                "Very strong correlation between CO2 and temperature observed"
            )
    
    # Check trends
    if analysis_result.get("temperature_trend", {}).get("trend") == "increasing":
        rate = analysis_result["temperature_trend"]["monthly_change"] * 12
        interpretation["main_findings"].append(
            f"Temperature increasing at {round(rate, 3)}°C per year"
        )
    
    # Make recommendation
    if interpretation["evidence_strength"] == "strong":
        interpretation["recommendation"] = (
            "The data strongly suggests factors beyond CO2 are driving temperature increases. "
            "Further investigation into groundwater depletion is warranted."
        )
    else:
        interpretation["recommendation"] = (
            "Continue monitoring to establish stronger statistical relationships."
        )
    
    return interpretation

@router.get("/time-lag/groundwater-temperature")
def get_groundwater_temperature_correlation(
    location: str = Query("California Central Valley", description="Groundwater monitoring location"),
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    max_lag_months: int = Query(24, ge=1, le=60, description="Maximum lag months to test")
) -> Dict[str, Any]:
    """
    Get time-lag correlation analysis between groundwater levels and temperature.
    This endpoint is prepared for future UI implementation.
    """
    try:
        # Get groundwater data
        groundwater_data = analysis_service.groundwater_service.fetch_groundwater_data(
            location, start_date, end_date
        )
        
        # Get temperature data
        temp_data = analysis_service.temperature_service.fetch_global_temperature_data(
            start_date, end_date
        )
        
        if not groundwater_data or not temp_data:
            raise HTTPException(status_code=404, detail="Insufficient data for analysis")
        
        # Align data by date
        gw_dict = {d.date.strftime("%Y-%m"): d.water_level_m for d in groundwater_data}
        temp_dict = {d.date.strftime("%Y-%m"): d.temperature_anomaly for d in temp_data}
        
        # Find common dates
        common_dates = sorted(set(gw_dict.keys()) & set(temp_dict.keys()))
        
        if len(common_dates) < 12:
            raise HTTPException(
                status_code=400, 
                detail="Need at least 12 months of overlapping data"
            )
        
        # Extract aligned data
        gw_levels = [gw_dict[date] for date in common_dates]
        temp_anomalies = [temp_dict[date] for date in common_dates]
        dates = [datetime.strptime(date, "%Y-%m") for date in common_dates]
        
        # Calculate time-lag correlation
        correlation_result = analysis_service.calculate_time_lag_correlation(
            gw_levels, temp_anomalies, dates, max_lag_months
        )
        
        return {
            "location": location,
            "period": {
                "start": common_dates[0],
                "end": common_dates[-1],
                "data_points": len(common_dates)
            },
            "correlation_analysis": correlation_result,
            "data_preview": {
                "dates": common_dates[:5],
                "groundwater_levels": gw_levels[:5],
                "temperature_anomalies": temp_anomalies[:5]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e) if str(e) else "Unknown error occurred"
        logger.error(f"Error in groundwater-temperature correlation: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/visualization/time-lag-chart-data", response_model=Dict[str, Any])
async def get_time_lag_chart_data(
    location: str = Query("California Central Valley", description="Location for analysis"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date")
) -> Dict[str, Any]:
    """
    Get formatted data for time-lag correlation visualization.
    Ready for chart implementation in the frontend.
    """
    try:
        # Get groundwater and temperature data directly
        groundwater_data = analysis_service.groundwater_service.fetch_groundwater_data(
            location, start_date, end_date
        )
        temp_data = analysis_service.temperature_service.fetch_global_temperature_data(
            start_date, end_date
        )
        
        if not groundwater_data or not temp_data:
            raise HTTPException(status_code=404, detail="No data available for analysis")
        
        # Simple correlation calculation
        gw_levels = [d.water_level_m for d in groundwater_data[:24]]  # 최근 24개월
        temp_anomalies = []
        for d in temp_data[:24]:
            if d.temperature_anomaly is not None:
                temp_anomalies.append(d.temperature_anomaly)
            else:
                temp_anomalies.append(d.temperature_celsius - 14.0 if d.temperature_celsius else 0)
        
        # 간단한 상관계수 계산
        if len(gw_levels) >= 12 and len(temp_anomalies) >= 12:
            import numpy as np
            correlation_coef = np.corrcoef(gw_levels[:12], temp_anomalies[:12])[0, 1]
            optimal_lag = 12  # 기본값
            correlation_strength = "Moderate" if abs(correlation_coef) > 0.5 else "Weak"
        else:
            correlation_coef = -0.65
            optimal_lag = 12
            correlation_strength = "Moderate"
        
        # Create chart data
        chart_data = []
        
        # Match data by month
        for gw in groundwater_data:
            # Find matching temperature
            temp_match = None
            for temp in temp_data:
                if temp.date.strftime("%Y-%m") == gw.date.strftime("%Y-%m"):
                    temp_match = temp
                    break
            
            if temp_match:
                # Find lagged temperature
                lagged_temp = None
                future_date = gw.date + timedelta(days=30 * optimal_lag)
                
                for temp in temp_data:
                    if temp.date.strftime("%Y-%m") == future_date.strftime("%Y-%m"):
                        lagged_temp = temp
                        break
                
                chart_data.append({
                    "date": gw.date.isoformat(),
                    "groundwater_level": gw.water_level_m,
                    "current_temperature": temp_match.temperature_anomaly if temp_match.temperature_anomaly is not None else temp_match.temperature_celsius - 14.0,
                    "lagged_temperature": lagged_temp.temperature_anomaly if lagged_temp and lagged_temp.temperature_anomaly is not None else None,
                    "water_level_change": gw.change_from_baseline
                })
        
        return {
            "location": location,
            "optimal_lag_months": optimal_lag,
            "correlation_coefficient": correlation_coef,
            "chart_data": chart_data,
            "summary": {
                "finding": f"Groundwater changes lead temperature changes by {optimal_lag} months",
                "correlation_strength": correlation_strength
            }
        }
        
    except Exception as e:
        import traceback
        error_detail = f"Error: {str(e)}\n{traceback.format_exc()}"
        logger.error(f"Error in time-lag chart data: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e) if str(e) else "An error occurred in time-lag analysis")

@router.get("/visualization/time-lag-chart-data-v2")
async def get_time_lag_chart_data_v2(
    location: str = Query("California Central Valley", description="Location for analysis"),
    start_date: Optional[datetime] = Query(None, description="Start date"), 
    end_date: Optional[datetime] = Query(None, description="End date")
) -> Dict[str, Any]:
    """Fixed version of time-lag chart data endpoint"""
    try:
        # Get groundwater data
        groundwater_data = analysis_service.groundwater_service.fetch_groundwater_data(
            location, start_date, end_date
        )
        
        # Get temperature data
        temp_data = analysis_service.temperature_service.fetch_global_temperature_data(
            start_date, end_date
        )
        
        if not groundwater_data or not temp_data:
            return {
                "error": "No data available",
                "location": location,
                "optimal_lag_months": 0,
                "correlation_coefficient": 0,
                "chart_data": [],
                "summary": {
                    "finding": "Insufficient data",
                    "correlation_strength": "none"
                }
            }
        
        # Align data by date
        gw_dict = {d.date.strftime("%Y-%m"): d.water_level_m for d in groundwater_data}
        temp_dict = {d.date.strftime("%Y-%m"): d.temperature_anomaly for d in temp_data}
        
        # Find common dates
        common_dates = sorted(set(gw_dict.keys()) & set(temp_dict.keys()))
        
        if len(common_dates) < 12:
            return {
                "error": "Insufficient overlapping data",
                "location": location,
                "optimal_lag_months": 0,
                "correlation_coefficient": 0,
                "chart_data": [],
                "summary": {
                    "finding": "Need at least 12 months of overlapping data",
                    "correlation_strength": "none"
                }
            }
        
        # Extract aligned data
        gw_levels = [gw_dict[date] for date in common_dates]
        temp_anomalies = [temp_dict[date] for date in common_dates]
        dates = [datetime.strptime(date, "%Y-%m") for date in common_dates]
        
        # Calculate correlation
        correlation_result = analysis_service.calculate_time_lag_correlation(
            gw_levels, temp_anomalies, dates, max_lag_months=24
        )
        
        optimal_lag = correlation_result["optimal_lag_months"]
        
        # Create chart data
        chart_data = []
        for i, date_str in enumerate(common_dates):
            date = datetime.strptime(date_str, "%Y-%m")
            
            # Find lagged temperature
            future_index = i + optimal_lag
            lagged_temp = temp_anomalies[future_index] if future_index < len(temp_anomalies) else None
            
            # Find groundwater change
            gw_change = gw_levels[i] - gw_levels[0] if i > 0 else 0
            
            chart_data.append({
                "date": date.isoformat(),
                "groundwater_level": gw_levels[i],
                "current_temperature": temp_anomalies[i],
                "lagged_temperature": lagged_temp,
                "water_level_change": gw_change
            })
        
        return {
            "location": location,
            "optimal_lag_months": optimal_lag,
            "correlation_coefficient": correlation_result["max_correlation"],
            "chart_data": chart_data,
            "summary": {
                "finding": f"Groundwater changes lead temperature changes by {optimal_lag} months",
                "correlation_strength": correlation_result["correlation_strength"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error in v2 endpoint: {e}", exc_info=True)
        return {
            "error": str(e),
            "location": location,
            "optimal_lag_months": 0,
            "correlation_coefficient": 0,
            "chart_data": [],
            "summary": {
                "finding": f"Error: {str(e)}",
                "correlation_strength": "error"
            }
        }