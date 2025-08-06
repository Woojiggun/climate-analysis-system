# Time-lag Correlation Chart Implementation Summary

## 작업 완료 사항

### 1. Time-lag Chart 컴포넌트 구현
- **파일**: `frontend/src/components/TimeLagChart.tsx`
- **기능**:
  - Chart.js를 사용한 이중 축 차트 구현
  - 지하수 수위와 온도 이상치의 시간차 상관관계 시각화
  - 최적 시간차(optimal_lag_months) 표시
  - 상관계수(correlation_coefficient) 표시
  - Mock 데이터 폴백 기능

### 2. UI 컴포넌트 생성
- **Card 컴포넌트**: `frontend/src/components/ui/card.tsx`
- **Alert 컴포넌트**: `frontend/src/components/ui/alert.tsx`
- **lucide-react** 아이콘 라이브러리 설치 완료

### 3. Dashboard 통합
- **파일**: `frontend/src/pages/Dashboard.tsx`
- TimeLagChart를 메인 대시보드에 통합
- CO2GapChart와 함께 표시

### 4. 백엔드 엔드포인트
- **구현된 엔드포인트**:
  - `/api/analysis/time-lag/groundwater-temperature`
  - `/api/analysis/visualization/time-lag-chart-data`
- **Mock 엔드포인트**: `/api/analysis/visualization/time-lag-chart-data-mock`

## 기술적 특징

### 차트 구성
```javascript
// 두 개의 Y축 사용
- Y1축: 지하수 수위 (meters below surface) - 역방향 스케일
- Y2축: 온도 이상치 (°C)
- X축: 시간 (년-월)
```

### 데이터 구조
```typescript
interface TimeLagData {
  location: string;
  optimal_lag_months: number;
  correlation_coefficient: number;
  chart_data: Array<{
    date: string;
    groundwater_level: number;
    current_temperature: number;
    lagged_temperature: number | null;
    water_level_change: number;
  }>;
  summary: {
    finding: string;
    correlation_strength: string;
  };
}
```

## 현재 상태

### 작동하는 기능
- ✅ Chart.js 이중 축 차트 렌더링
- ✅ Mock 데이터로 시각화 표시
- ✅ 상관관계 통계 표시 (상관계수: -0.72)
- ✅ 최적 시간차 표시 (12개월)
- ✅ 반응형 디자인
- ✅ 에러 시 Mock 데이터 폴백

### 알려진 이슈
- ⚠️ 백엔드 API의 실제 데이터 연동 시 HTTPException detail 빈 문자열 반환
- ⚠️ 현재 Mock 데이터로 작동 중

## 사용 방법

### 프론트엔드 실행
```bash
cd frontend
npm install
npm start
```

### 백엔드 실행
```bash
cd backend
python main.py
```

### 브라우저 접속
- http://localhost:3000 접속
- Dashboard에서 Time-lag Correlation Analysis 차트 확인

## Mock 데이터 설명
- 지하수 수위: -30m에서 시작하여 점진적으로 감소 (고갈 시뮬레이션)
- 온도 이상치: 1.0°C에서 시작하여 상승 추세
- 시간차: 12개월 (지하수 변화가 온도 변화를 12개월 선행)
- 상관계수: -0.72 (강한 음의 상관관계)

## 다음 단계 권장사항

1. **백엔드 API 수정**
   - HTTPException detail 처리 개선
   - 실제 상관관계 계산 로직 디버깅

2. **USGS API 통합**
   - 실제 지하수 데이터 수집
   - API 키 획득 및 연동

3. **UI 개선**
   - 날짜 범위 선택기 추가
   - 지역 선택 드롭다운 구현
   - 데이터 내보내기 기능

4. **프로젝트 문서화**
   - 기술 문서 작성
   - API 사용 가이드
   - 시스템 아키텍처 다이어그램