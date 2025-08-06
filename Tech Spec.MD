
## 📋 **Claude Code 전달용 완성 명세서**

---

# 🌍 CO₂-Groundwater-Temperature Climate Analysis System

## 📌 **프로젝트 개요**

**핵심 가설**: CO₂ 증가만으로는 설명할 수 없는 온도 상승이 존재하며, 그 원인은 지하수 고갈에 있다.

**목표**: 과학적 데이터 분석을 통해 이 가설을 증명하고, 인터랙티브 웹 시스템으로 시각화

---

## 🎯 **우선순위 기반 개발 계획**

### **Priority 1 (Critical) - Day 1-3**
- [ ] 프로젝트 구조 설정
- [ ] 진행 추적 대시보드 생성
- [ ] 기본 데이터 수집 (CO₂, 온도)
- [ ] CO₂ Gap 분석 핵심 알고리즘
- [ ] CO₂ Gap Chart 시각화

### **Priority 2 (Important) - Day 4-6** 
- [ ] 지하수 데이터 수집
- [ ] Time-lag 상관관계 분석
- [ ] 기본 웹 인터페이스 구축
- [ ] Evidence Section 구현

### **Priority 3 (Nice-to-have) - Day 7-10**
- [ ] 지역별 차별화 분석
- [ ] 복합 모델 검증
- [ ] 인터랙티브 기능 고도화
- [ ] 최종 완성도 높이기

---

## 🛠️ **기술 스택**

### **Backend**
- Python 3.9+
- FastAPI (REST API)
- Pandas, NumPy (데이터 분석)
- SciPy, Scikit-learn (통계 분석)
- SQLite (데이터 저장)

### **Frontend**
- React.js + TypeScript
- Chart.js / D3.js (시각화)
- Tailwind CSS (스타일링)
- Axios (API 통신)

### **배포**
- Frontend: Vercel/Netlify
- Backend: Railway/Heroku

---

## 📊 **데이터 소스**

```python
data_sources = {
    "co2_data": {
        "source": "NOAA Global Monitoring Laboratory",
        "url": "https://gml.noaa.gov/ccgg/trends/data.html",
        "format": "CSV/JSON",
        "period": "2000-2024"
    },
    "temperature_data": {
        "source": "NASA GISS Surface Temperature Analysis",
        "url": "https://data.giss.nasa.gov/gistemp/",
        "format": "NetCDF/CSV", 
        "resolution": "monthly, regional"
    },
    "groundwater_data": {
        "source": "USGS Water Resources",
        "url": "https://waterdata.usgs.gov/nwis",
        "format": "JSON API",
        "metrics": "water_table_depth, storage_change"
    }
}
```

---

## 🔬 **핵심 알고리즘 명세**

### **1. CO₂ Gap Analyzer (Priority 1)**
```python
def co2_gap_analyzer(co2_ppm, actual_temp, region_id):
    """
    CO₂ 농도 기반 이론적 온도 vs 실제 온도 차이 분석
    
    Args:
        co2_ppm: CO₂ 농도 (ppm)
        actual_temp: 실제 측정 온도 (°C)
        region_id: 지역 식별자
        
    Returns:
        dict: {
            "theoretical_temp": float,
            "actual_temp": float,
            "unexplained_gap": float,
            "gap_percentage": float,
            "p_value": float,
            "confidence_interval": tuple
        }
    """
    # 이론적 온도 계산 (IPCC AR6 기준)
    baseline_co2 = 315  # 1958년 기준
    climate_sensitivity = 3.0  # °C per CO₂ doubling
    
    theoretical_temp = climate_sensitivity * np.log2(co2_ppm / baseline_co2)
    temperature_gap = actual_temp - theoretical_temp
    
    # 통계적 유의성 검증
    t_stat, p_value = stats.ttest_1samp([temperature_gap], 0)
    ci_95 = stats.t.interval(0.95, len([temperature_gap])-1, 
                           loc=np.mean([temperature_gap]),
                           scale=stats.sem([temperature_gap]))
    
    return {
        "theoretical_temp": theoretical_temp,
        "actual_temp": actual_temp,
        "unexplained_gap": temperature_gap,
        "gap_percentage": (temperature_gap / theoretical_temp) * 100,
        "p_value": p_value,
        "confidence_interval": ci_95
    }
```

### **2. Time-Lag Analysis (Priority 2)**
```python
def groundwater_temperature_lag_analysis(gw_data, temp_data, max_lag=24):
    """
    지하수 변화와 온도 변화 간 시차 상관관계 분석
    
    Args:
        gw_data: 지하수 레벨 시계열 데이터
        temp_data: 온도 시계열 데이터  
        max_lag: 최대 지연 개월 수
        
    Returns:
        dict: {
            "optimal_lag_months": int,
            "max_correlation": float,
            "lag_correlation_series": dict,
            "lead_relationship": bool
        }
    """
    correlations = {}
    
    for lag in range(0, max_lag + 1):
        # 지하수 데이터를 lag만큼 shift
        gw_shifted = gw_data.shift(-lag).dropna()
        temp_aligned = temp_data.loc[gw_shifted.index]
        
        # 상관계수 계산
        correlation, p_value = stats.pearsonr(gw_shifted, temp_aligned)
        correlations[lag] = {
            "correlation": correlation,
            "p_value": p_value
        }
    
    # 최대 상관관계 찾기
    optimal_lag = max(correlations.keys(), 
                     key=lambda x: abs(correlations[x]["correlation"]))
    
    return {
        "optimal_lag_months": optimal_lag,
        "max_correlation": correlations[optimal_lag]["correlation"],
        "lag_correlation_series": correlations,
        "lead_relationship": optimal_lag > 0
    }
```

---

## 🌐 **웹 인터페이스 구조**

### **페이지 구성**
```javascript
app_structure = {
    "/": {
        component: "LandingPage",
        sections: ["Hero", "KeyFindings", "CallToAction"]
    },
    "/evidence": {
        component: "EvidencePage", 
        tabs: [
            "CO₂ Gap Analysis",
            "Time-Lag Correlation", 
            "Regional Differences",
            "Model Comparison"
        ]
    },
    "/analysis": {
        component: "InteractiveAnalysis",
        features: ["Region Selector", "Time Range", "Custom Analysis"]
    },
    "/about": {
        component: "AboutPage",
        sections: ["Methodology", "Data Sources", "Team"]
    }
}
```

### **핵심 컴포넌트**
```javascript
// Priority 1 컴포넌트
components = {
    "CO2GapChart": {
        type: "area_chart",
        data_source: "/api/co2-gap-analysis",
        features: ["zoom", "tooltip", "export"]
    },
    "ProgressTracker": {
        type: "dashboard", 
        sections: ["overall", "phase_breakdown", "current_task"],
        update_frequency: "real-time"
    }
}
```

---

## 📈 **진행 상황 추적 시스템**

### **Task Breakdown**
```markdown
## Phase 1: 핵심 증명 (Day 1-3)
- [ ] 프로젝트 구조 및 진행 추적 대시보드 (4h)
- [ ] CO₂ 데이터 수집 API (3h)
- [ ] 온도 데이터 수집 API (3h)
- [ ] CO₂ Gap 분석 알고리즘 (5h)
- [ ] 기본 웹 인터페이스 (4h)
- [ ] CO₂ Gap Chart 구현 (4h)

Total: 6 tasks, 23 hours

## Phase 2: 증거 확장 (Day 4-6)  
- [ ] 지하수 데이터 수집 (4h)
- [ ] Time-lag 분석 알고리즘 (6h)
- [ ] Evidence Section UI (4h)
- [ ] Lag Correlation 시각화 (4h)
- [ ] API 통합 및 테스트 (3h)

Total: 5 tasks, 21 hours

## Phase 3: 완성도 (Day 7-10)
- [ ] 지역별 차별화 분석 (6h)
- [ ] 복합 모델 검증 (5h)
- [ ] 인터랙티브 분석 도구 (8h)  
- [ ] 모바일 최적화 (4h)
- [ ] 최종 테스트 및 배포 (5h)

Total: 5 tasks, 28 hours
```

### **Progress Dashboard 명세**
```javascript
// public/progress-tracker.html에 구현
progress_config = {
    overall_progress: {
        total_tasks: 16,
        completed: 0,
        current_phase: "Phase 1"
    },
    
    daily_targets: [
        {day: 1, tasks: 2, hours: 8},
        {day: 2, tasks: 2, hours: 8}, 
        {day: 3, tasks: 2, hours: 7},
        // ... 10일간
    ],
    
    current_task: {
        name: "프로젝트 구조 설정",
        estimated_hours: 4,
        start_time: null,
        status: "not_started"
    }
}
```

---

## 🎯 **첫 번째 작업 요청**

### **즉시 시작할 작업:**
1. **프로젝트 구조 생성** + **진행 추적 대시보드**
2. **CO₂ 데이터 수집 모듈** 구현
3. **CO₂ Gap 분석 알고리즘** 구현  
4. **기본 시각화** (CO₂ Gap Chart)

**예상 소요시간**: 15-20시간
**완료 목표**: Day 3 end
**성공 지표**: 작동하는 CO₂ Gap 분석 + 웹에서 차트 확인

---

## 📞 **소통 및 피드백**

### **작업 중 확인사항:**
- 데이터 수집 시 접근 제한 문제
- 알고리즘 구현 중 통계적 검증 방법
- 시각화 라이브러리 선택 (Chart.js vs D3.js)
- 성능 최적화 필요 지점

### **중간 체크포인트:**
- Day 1 end: 프로젝트 구조 + 진행 추적
- Day 2 end: 데이터 수집 + 기본 분석
- Day 3 end: 시각화 + 웹 인터페이스

