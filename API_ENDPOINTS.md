# Climate Analysis System API Endpoints

## 기본 정보
- Base URL: `http://localhost:8000`
- 모든 날짜는 ISO 8601 형식 사용 (예: 2024-01-01T00:00:00)

## 구현 완료된 엔드포인트

### CO₂ 데이터
- `GET /api/co2/monthly` - 월별 CO₂ 데이터
- `GET /api/co2/daily` - 일별 CO₂ 데이터  
- `GET /api/co2/latest` - 최신 CO₂ 데이터
- `GET /api/co2/summary` - CO₂ 데이터 요약 통계

### 온도 데이터
- `GET /api/temperature/global` - 전 세계 온도 데이터
- `GET /api/temperature/regional/{region}` - 지역별 온도 데이터
- `GET /api/temperature/latest` - 최신 온도 데이터
- `GET /api/temperature/summary` - 온도 데이터 요약 통계
- `GET /api/temperature/compare` - 지역 간 온도 비교

### 지하수 데이터
- `GET /api/groundwater/data` - 지하수 수위 데이터
- `GET /api/groundwater/locations` - 사용 가능한 지역 목록
- `GET /api/groundwater/summary` - 지하수 데이터 요약
- `GET /api/groundwater/regional-comparison` - 지역별 비교
- `POST /api/groundwater/correlation-data` - 상관관계 분석용 데이터

### 분석 엔드포인트
- `GET /api/analysis/co2-gap` - CO₂ Gap 분석
- `POST /api/analysis/co2-gap/calculate` - 단일 지점 CO₂ Gap 계산
- `GET /api/analysis/co2-gap/summary` - CO₂ Gap 요약 통계
- `POST /api/analysis/time-lag/correlation` - Time-lag 상관관계 분석
- `GET /api/analysis/trends/comprehensive` - 종합 분석

## 다음 작업을 위해 준비된 엔드포인트

### Time-lag 상관관계 시각화
- `GET /api/analysis/time-lag/groundwater-temperature`
  - 지하수-온도 간 시간차 상관관계 분석
  - UI 구현 시 바로 사용 가능

- `GET /api/analysis/visualization/time-lag-chart-data`
  - 차트 구현을 위한 포맷된 데이터
  - optimal_lag_months, correlation_coefficient 포함

### USGS 통합 준비
- `GET /api/groundwater/usgs/sites`
  - USGS 모니터링 사이트 목록 (placeholder)
  - 실제 USGS API 연동 준비됨

- `GET /api/groundwater/usgs/data/{site_id}`
  - 특정 사이트의 지하수 데이터 (placeholder)
  - USGS NWIS API 형식 맞춤

## 사용 예시

### CO₂ Gap 분석 데이터 가져오기
```javascript
const response = await axios.get('http://localhost:8000/api/analysis/co2-gap', {
    params: {
        start_date: '2022-01-01T00:00:00',
        end_date: '2025-12-31T23:59:59'
    }
});
```

### Time-lag 차트 데이터 가져오기
```javascript
const response = await axios.get('http://localhost:8000/api/analysis/visualization/time-lag-chart-data', {
    params: {
        location: 'California Central Valley',
        start_date: '2020-01-01T00:00:00'
    }
});
```

## 다음 작업 가이드

### 1. Time-lag 상관관계 차트 UI 구현
- `/api/analysis/visualization/time-lag-chart-data` 엔드포인트 사용
- Chart.js로 이중 축 차트 구현 (지하수 수위 + 지연된 온도)
- optimal_lag_months를 UI에 표시

### 2. USGS API 실제 연동
- USGS API 키 획득 필요
- `/api/groundwater/usgs/sites`와 `/api/groundwater/usgs/data/{site_id}` 구현
- GroundwaterDataService에 USGS API 호출 로직 추가

### 3. 프로젝트 문서화
- 기술 문서 작성
- API 사용 가이드
- 시스템 아키텍처 다이어그램