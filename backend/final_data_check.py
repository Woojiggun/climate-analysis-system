import asyncio
from datetime import datetime
from services.co2_service import CO2DataService
from services.temperature_service import TemperatureDataService
from services.analysis_service import AnalysisService

async def final_check():
    print("=== Final Data Verification ===\n")
    
    # 1. 최신 데이터 범위 확인
    co2_service = CO2DataService()
    temp_service = TemperatureDataService()
    
    # 모든 데이터 가져오기
    co2_data = co2_service.fetch_monthly_co2_data()
    temp_data = temp_service.fetch_global_temperature_data()
    
    print("1. Data Range:")
    if co2_data:
        print(f"   CO2: {co2_data[0].date.strftime('%Y-%m')} to {co2_data[-1].date.strftime('%Y-%m')}")
        print(f"   Latest CO2: {co2_data[-1].ppm} ppm")
    
    if temp_data:
        print(f"   Temperature: {temp_data[0].date.strftime('%Y-%m')} to {temp_data[-1].date.strftime('%Y-%m')}")
        print(f"   Latest temp: {temp_data[-1].temperature_celsius}°C (anomaly: {temp_data[-1].temperature_anomaly}°C)")
    
    # 2. 2024년 데이터 확인
    print("\n2. 2024 Monthly Data:")
    analysis_service = AnalysisService()
    gap_data = await analysis_service.analyze_co2_temperature_gap(
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 11, 30)
    )
    
    if gap_data:
        print("   Month | CO2(ppm) | Actual(°C) | Theory(°C) | Gap(°C)")
        print("   ------|----------|------------|------------|--------")
        for data in gap_data:
            print(f"   {data.date.strftime('%b')}   | {data.co2_ppm:7.2f} | {data.actual_temp:10.2f} | {data.theoretical_temp:10.2f} | {data.unexplained_gap:7.2f}")
    
    # 3. Gap 분석 요약
    if gap_data:
        avg_gap = sum(d.unexplained_gap for d in gap_data) / len(gap_data)
        avg_pct = sum(d.gap_percentage for d in gap_data) / len(gap_data)
        print(f"\n3. Summary:")
        print(f"   Average gap: {avg_gap:.2f}°C")
        print(f"   Average gap percentage: {avg_pct:.1f}%")
        print(f"   Conclusion: {avg_pct:.1f}% of warming cannot be explained by CO2 alone")

if __name__ == "__main__":
    asyncio.run(final_check())