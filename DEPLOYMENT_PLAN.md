# Climate Analysis System - 배포 계획

## 현재 상태
- ✅ Backend: Python/FastAPI 완성
- ✅ 임시 Frontend: demo.html (순수 HTML/JS)
- ❌ Production Frontend: React/TypeScript (필요)
- ❌ 배포 설정: Docker, CI/CD (필요)

## React 프론트엔드 구축 계획

### 1. 프로젝트 구조
```
climate-analysis-system/
├── backend/              # 현재 완성된 FastAPI 백엔드
├── frontend/            # 새로 만들 React 앱
│   ├── src/
│   │   ├── components/
│   │   │   ├── Charts/
│   │   │   │   ├── CO2GapChart.tsx
│   │   │   │   ├── TemperatureTrendChart.tsx
│   │   │   │   └── TimeLagChart.tsx
│   │   │   ├── Dashboard/
│   │   │   │   ├── StatsCard.tsx
│   │   │   │   └── Dashboard.tsx
│   │   │   └── Layout/
│   │   │       ├── Header.tsx
│   │   │       └── Navigation.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── co2Service.ts
│   │   │   ├── temperatureService.ts
│   │   │   └── analysisService.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   └── tsconfig.json
├── docker-compose.yml
└── .github/
    └── workflows/
        └── deploy.yml
```

### 2. 주요 기술 스택
- React 18 + TypeScript
- Chart.js (이미 사용 중)
- Axios (API 통신)
- TailwindCSS (스타일링)
- Vite (빌드 도구)

### 3. React 컴포넌트 계획

#### CO2GapChart.tsx
```typescript
interface CO2GapChartProps {
  startDate: string;
  endDate: string;
}

export const CO2GapChart: React.FC<CO2GapChartProps> = ({ startDate, endDate }) => {
  // 현재 demo.html의 createGapChart 로직 이관
};
```

#### Dashboard.tsx
```typescript
export const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'gap' | 'trend' | 'timelag'>('gap');
  
  return (
    <div className="container mx-auto p-4">
      <StatsGrid />
      <TabNavigation activeTab={activeTab} onChange={setActiveTab} />
      {activeTab === 'gap' && <CO2GapChart />}
      {activeTab === 'trend' && <TemperatureTrendChart />}
      {activeTab === 'timelag' && <TimeLagChart />}
    </div>
  );
};
```

## GitHub 배포 설정

### 1. Docker 설정
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# frontend/Dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

### 2. docker-compose.yml
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - NASA_API_KEY=${NASA_API_KEY}
      - CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
    
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://backend:8000
```

### 3. GitHub Actions CI/CD
```yaml
# .github/workflows/deploy.yml
name: Deploy Climate Analysis System

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and push Docker images
        run: |
          docker build -t climate-backend ./backend
          docker build -t climate-frontend ./frontend
          
      - name: Deploy to server
        # SSH 배포 또는 cloud provider 배포
```

## 배포 옵션

### 1. GitHub Pages (프론트엔드만)
- 정적 사이트로 빌드하여 GitHub Pages에 배포
- 백엔드는 별도 호스팅 필요

### 2. Vercel/Netlify (프론트엔드) + Railway/Render (백엔드)
- 프론트엔드: Vercel 또는 Netlify로 자동 배포
- 백엔드: Railway 또는 Render.com으로 배포

### 3. AWS/GCP/Azure (풀스택)
- EC2/Compute Engine에 Docker Compose로 전체 배포
- 또는 각 서비스별 관리형 서비스 사용

### 4. 추천: Vercel + Railway
- 가장 간단하고 무료 티어 제공
- 자동 CI/CD 지원
- HTTPS 자동 설정

## 환경 변수 설정
```bash
# .env.production
REACT_APP_API_URL=https://api.climate-analysis.com
NASA_API_KEY=your_actual_key
USGS_API_KEY=your_actual_key
```

## 다음 단계
1. React 프로젝트 생성 및 기본 구조 설정
2. demo.html의 로직을 React 컴포넌트로 이관
3. Docker 설정 및 테스트
4. GitHub 저장소 생성 및 CI/CD 설정
5. 도메인 연결 및 HTTPS 설정