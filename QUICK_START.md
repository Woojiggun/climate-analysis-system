# 🚀 Climate Analysis System - Quick Start Guide

## 시스템 실행 방법

### 1. 백엔드 서버 실행
```bash
cd backend
python main.py
```
또는 Windows에서: `start-backend.bat` 실행

백엔드가 실행되면 다음 메시지가 표시됩니다:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. 데모 UI 실행 (간단한 방법)
1. 백엔드가 실행 중인지 확인
2. `demo.html` 파일을 웹 브라우저로 열기
3. 실시간 데이터와 차트를 확인

### 3. React 프론트엔드 실행 (전체 버전)
```bash
cd frontend
npm install --legacy-peer-deps
npm start
```
또는 Windows에서: `start-frontend.bat` 실행

## 주요 기능 확인

### API 테스트
브라우저에서 다음 URL들을 방문하여 API가 작동하는지 확인:
- http://localhost:8000 - API 상태 확인
- http://localhost:8000/api/co2/latest - 최신 CO2 데이터
- http://localhost:8000/api/temperature/latest - 최신 온도 데이터
- http://localhost:8000/docs - 자동 생성된 API 문서 (Swagger UI)

### 진행 상황 추적
`progress-tracker.html` 파일을 브라우저로 열어 프로젝트 진행 상황 확인

## 트러블슈팅

### 백엔드가 실행되지 않을 때
1. Python 3.9 이상이 설치되어 있는지 확인
2. 필요한 패키지 설치:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

### 프론트엔드 설치 오류
1. Node.js 16 이상이 설치되어 있는지 확인
2. 캐시 정리 후 재설치:
   ```bash
   npm cache clean --force
   npm install --legacy-peer-deps
   ```

### CORS 오류
백엔드가 http://localhost:8000 에서 실행 중인지 확인

## 데이터 소스
- CO2 데이터: NOAA Mauna Loa Observatory
- 온도 데이터: NASA GISS
- 실시간 데이터는 인터넷 연결이 필요합니다

## 문의사항
프로젝트 관련 문의는 GitHub Issues를 통해 남겨주세요.