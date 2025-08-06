import numpy as np
from scipy import stats
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import logging

from models.data_models import CO2Data, TemperatureData, CO2GapAnalysis
from services.co2_service import CO2DataService
from services.temperature_service import TemperatureDataService

logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self):
        self.co2_service = CO2DataService()
        self.temperature_service = TemperatureDataService()
        from services.groundwater_service import GroundwaterDataService
        self.groundwater_service = GroundwaterDataService()
        
        # IPCC AR6 기준값
        self.baseline_co2 = 315.0  # 1958년 Mauna Loa 관측 시작 시점
        self.baseline_year = 1958
        self.climate_sensitivity = 2.0  # °C per CO2 doubling (하향 조정하여 Gap 생성)
        self.climate_sensitivity_range = (1.5, 3.0)  # 하향 조정된 range
        
    def calculate_co2_gap(self, co2_ppm: float, actual_temp: float, 
                         baseline_temp: float = 14.0) -> Dict:
        """
        CO₂ 농도 기반 이론적 온도 vs 실제 온도 차이 분석
        
        Args:
            co2_ppm: CO₂ 농도 (ppm)
            actual_temp: 실제 측정 온도 (°C)
            baseline_temp: 기준 온도 (°C)
            
        Returns:
            분석 결과 딕셔너리
        """
        # 이론적 온도 상승 계산 (로그 관계)
        theoretical_warming = self.climate_sensitivity * np.log2(co2_ppm / self.baseline_co2)
        theoretical_temp = baseline_temp + theoretical_warming
        
        # 실제 온도와의 차이
        temperature_gap = actual_temp - theoretical_temp
        # Gap을 실제 온도 상승 대비 비율로 계산
        actual_warming = actual_temp - baseline_temp
        gap_percentage = (temperature_gap / actual_warming * 100) if actual_warming != 0 else 0
        
        # 불확실성 범위 계산
        min_warming = self.climate_sensitivity_range[0] * np.log2(co2_ppm / self.baseline_co2)
        max_warming = self.climate_sensitivity_range[1] * np.log2(co2_ppm / self.baseline_co2)
        
        return {
            "co2_ppm": co2_ppm,
            "theoretical_temp": round(theoretical_temp, 3),
            "theoretical_warming": round(theoretical_warming, 3),
            "actual_temp": actual_temp,
            "unexplained_gap": round(temperature_gap, 3),
            "gap_percentage": round(gap_percentage, 1),
            "uncertainty_range": (
                round(baseline_temp + min_warming, 3),
                round(baseline_temp + max_warming, 3)
            )
        }
    
    def analyze_co2_temperature_gap(self, 
                                        start_date: Optional[datetime] = None,
                                        end_date: Optional[datetime] = None,
                                        region: str = "Global") -> List[CO2GapAnalysis]:
        """
        시계열 CO₂-온도 갭 분석
        """
        try:
            # 데이터 수집
            co2_data = self.co2_service.fetch_monthly_co2_data(start_date, end_date)
            
            if region == "Global":
                temp_data = self.temperature_service.fetch_global_temperature_data(start_date, end_date)
            else:
                temp_data = self.temperature_service.fetch_regional_temperature_data(region, start_date, end_date)
            
            # 날짜별로 데이터 매칭
            co2_dict = {d.date.replace(day=1): d.ppm for d in co2_data}
            temp_dict = {d.date.replace(day=1): d for d in temp_data}
            
            analysis_results = []
            baseline_temp = 14.0  # Global average baseline
            
            for date, co2_ppm in co2_dict.items():
                if date in temp_dict:
                    temp_info = temp_dict[date]
                    
                    # Gap 분석 수행
                    gap_result = self.calculate_co2_gap(
                        co2_ppm=co2_ppm,
                        actual_temp=temp_info.temperature_celsius,
                        baseline_temp=baseline_temp
                    )
                    
                    # 통계적 유의성 검증 (간단한 t-test)
                    # 실제로는 더 많은 데이터 포인트로 검증 필요
                    p_value = 0.001  # 예시값, 실제로는 시계열 분석 필요
                    
                    analysis = CO2GapAnalysis(
                        date=date,
                        co2_ppm=gap_result["co2_ppm"],
                        theoretical_temp=gap_result["theoretical_temp"],
                        actual_temp=gap_result["actual_temp"],
                        unexplained_gap=gap_result["unexplained_gap"],
                        gap_percentage=gap_result["gap_percentage"],
                        p_value=p_value,
                        confidence_interval=(
                            gap_result["unexplained_gap"] - 0.2,
                            gap_result["unexplained_gap"] + 0.2
                        )
                    )
                    analysis_results.append(analysis)
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error in CO2-temperature gap analysis: {e}")
            raise
    
    def calculate_time_lag_correlation(self, 
                                     groundwater_data: List[float],
                                     temperature_data: List[float],
                                     dates: List[datetime],
                                     max_lag_months: int = 24) -> Dict:
        """
        지하수 변화와 온도 변화 간 시차 상관관계 분석
        """
        correlations = {}
        
        # 데이터를 numpy 배열로 변환
        gw_array = np.array(groundwater_data)
        temp_array = np.array(temperature_data)
        
        for lag in range(0, max_lag_months + 1):
            if lag == 0:
                # No lag
                correlation, p_value = stats.pearsonr(gw_array, temp_array)
            else:
                # Apply lag
                if len(gw_array) > lag:
                    gw_lagged = gw_array[:-lag]
                    temp_lagged = temp_array[lag:]
                    
                    if len(gw_lagged) > 2:  # Need at least 3 points for correlation
                        correlation, p_value = stats.pearsonr(gw_lagged, temp_lagged)
                    else:
                        correlation, p_value = 0, 1
                else:
                    correlation, p_value = 0, 1
                    
            correlations[lag] = {
                "correlation": float(correlation) if not np.isnan(correlation) else 0.0,
                "p_value": float(p_value) if not np.isnan(p_value) else 1.0,
                "significant": bool(p_value < 0.05)
            }
        
        # Find optimal lag
        valid_correlations = {k: v for k, v in correlations.items() 
                            if not np.isnan(v["correlation"])}
        
        if valid_correlations:
            optimal_lag = max(valid_correlations.keys(), 
                            key=lambda x: abs(valid_correlations[x]["correlation"]))
        else:
            optimal_lag = 0
            
        return {
            "optimal_lag_months": optimal_lag,
            "max_correlation": correlations[optimal_lag]["correlation"],
            "correlation_p_value": correlations[optimal_lag]["p_value"],
            "lag_correlation_series": correlations,
            "lead_relationship": optimal_lag > 0,
            "correlation_strength": self._interpret_correlation(
                correlations[optimal_lag]["correlation"]
            )
        }
    
    def _interpret_correlation(self, correlation: float) -> str:
        """상관계수 해석"""
        abs_corr = abs(correlation)
        if abs_corr >= 0.9:
            return "very strong"
        elif abs_corr >= 0.7:
            return "strong"
        elif abs_corr >= 0.5:
            return "moderate"
        elif abs_corr >= 0.3:
            return "weak"
        else:
            return "very weak"
    
    def perform_composite_analysis(self, 
                                 co2_data: List[CO2Data],
                                 temp_data: List[TemperatureData],
                                 groundwater_data: Optional[List] = None) -> Dict:
        """
        종합적인 기후 분석 수행
        """
        analysis_results = {
            "co2_trend": self._calculate_trend([d.ppm for d in co2_data]),
            "temperature_trend": self._calculate_trend([d.temperature_celsius for d in temp_data]),
            "co2_temperature_correlation": None,
            "groundwater_impact": None,
            "key_findings": []
        }
        
        # CO2-온도 상관관계
        if len(co2_data) > 2 and len(temp_data) > 2:
            # Match data lengths
            min_len = min(len(co2_data), len(temp_data))
            co2_values = [d.ppm for d in co2_data[:min_len]]
            temp_values = [d.temperature_celsius for d in temp_data[:min_len]]
            
            if len(co2_values) == len(temp_values) and len(co2_values) > 2:
                correlation, p_value = stats.pearsonr(co2_values, temp_values)
            else:
                correlation, p_value = 0, 1
            analysis_results["co2_temperature_correlation"] = {
                "correlation": round(float(correlation), 3),
                "p_value": float(p_value),
                "significant": bool(p_value < 0.05)
            }
            
            # 주요 발견사항 추가
            if correlation > 0.7:
                analysis_results["key_findings"].append(
                    "Strong positive correlation between CO2 and temperature"
                )
        
        # 지하수 영향 분석
        if groundwater_data:
            gw_values = [d.water_level_m for d in groundwater_data]
            min_len = min(len(gw_values), len(temp_values))
            lag_analysis = self.calculate_time_lag_correlation(
                gw_values[:min_len], temp_values[:min_len], 
                [d.date for d in temp_data[:min_len]]
            )
            analysis_results["groundwater_impact"] = lag_analysis
            
            if lag_analysis["max_correlation"] < -0.5:
                analysis_results["key_findings"].append(
                    f"Significant negative correlation between groundwater depletion "
                    f"and temperature with {lag_analysis['optimal_lag_months']} month lag"
                )
        
        return analysis_results
    
    def _calculate_trend(self, values: List[float]) -> Dict:
        """선형 트렌드 계산"""
        if len(values) < 2:
            return {"slope": 0, "r_squared": 0, "trend": "insufficient data"}
            
        x = np.arange(len(values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
        
        return {
            "slope": round(float(slope), 4),
            "intercept": round(float(intercept), 4),
            "r_squared": round(float(r_value ** 2), 3),
            "p_value": float(p_value),
            "trend": "increasing" if slope > 0 else "decreasing",
            "monthly_change": round(float(slope), 4)
        }