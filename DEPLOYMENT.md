# 롤다방 내전프로그램 배포 가이드

## 목차
- [개요](#개요)
- [백엔드 배포 (Railway)](#백엔드-배포-railway)
- [프론트엔드 배포 (Vercel)](#프론트엔드-배포-vercel)
- [로컬 개발 환경](#로컬-개발-환경)
- [문제 해결](#문제-해결)

---

## 개요

이 프로젝트는 백엔드와 프론트엔드를 별도로 배포합니다:
- **백엔드**: Railway (영구 스토리지 지원)
- **프론트엔드**: Vercel (정적 사이트 호스팅)
- **연결**: Vercel 환경 변수를 통해 Railway 백엔드 URL 설정

---

## 백엔드 배포 (Railway)

### 사전 준비
1. [Railway](https://railway.app) 계정 생성
2. GitHub 계정과 Railway 연동

### 배포 방법

#### Option 1: GitHub 연동 자동 배포 (권장)

1. **GitHub에 코드 푸시**
   ```bash
   git add .
   git commit -m "Backend deployment setup"
   git push origin main
   ```

2. **Railway 대시보드에서 설정**
   - [Railway 대시보드](https://railway.app/dashboard) 접속
   - "New Project" 클릭
   - "Deploy from GitHub repo" 선택
   - 저장소 선택 후 `backend` 디렉토리 지정

3. **서비스 설정**
   - **Root Directory**: `backend`
   - **Build Command**: (자동 감지됨)
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **영구 볼륨 추가**
   - 프로젝트 대시보드에서 서비스 선택
   - "Variables" 탭 클릭
   - "New Volume" 클릭
   - Mount Path: `/data`
   - 저장 후 서비스 재시작

5. **환경 변수 설정**
   - `PORT`: 8000 (Railway가 자동 설정)
   - Railway는 `RAILWAY_ENVIRONMENT` 자동 설정

6. **도메인 확인**
   - "Settings" 탭에서 "Public Networking" 섹션 확인
   - "Generate Domain" 클릭
   - 생성된 URL 복사 (예: `https://your-app.railway.app`)

#### Option 2: Railway CLI 사용

1. **Railway CLI 설치**
   ```bash
   npm install -g @railway/cli
   ```

2. **로그인**
   ```bash
   railway login
   ```

3. **프로젝트 초기화**
   ```bash
   cd backend
   railway init
   ```

4. **배포**
   ```bash
   railway up
   ```

5. **도메인 생성**
   ```bash
   railway domain
   ```

### 헬스체크
배포 후 다음 URL에 접속하여 백엔드가 정상 작동하는지 확인:
```
https://your-app.railway.app/api/health
```

응답 예시:
```json
{
  "status": "ok",
  "database": "connected"
}
```

---

## 프론트엔드 배포 (Vercel)

### 사전 준비
1. [Vercel](https://vercel.com) 계정 생성
2. Vercel CLI 설치:
   ```bash
   npm install -g vercel
   ```

### 배포 방법

#### Option 1: Vercel CLI 사용

1. **프론트엔드 빌드**
   ```bash
   cd frontend
   npm run build
   ```

2. **빌드 결과를 public 폴더로 복사**
   ```bash
   # PowerShell
   Copy-Item -Path "frontend\dist\*" -Destination "public" -Recurse -Force
   
   # Bash
   cp -r frontend/dist/* public/
   ```

3. **Vercel 배포**
   ```bash
   vercel --prod
   ```

#### Option 2: Vercel 대시보드 사용

1. [Vercel 대시보드](https://vercel.com/dashboard) 접속
2. "Add New Project" 클릭
3. GitHub 저장소 선택
4. 프로젝트 설정:
   - **Framework Preset**: Other
   - **Build Command**: `cd frontend && npm run build && cp -r dist/* ../public/`
   - **Output Directory**: `public`

### 환경 변수 설정

**중요**: Vercel 대시보드에서 환경 변수를 설정해야 합니다.

1. Vercel 프로젝트 페이지에서 "Settings" 탭 클릭
2. "Environment Variables" 섹션으로 이동
3. 다음 환경 변수 추가:
   - **Name**: `VITE_API_BASE_URL`
   - **Value**: Railway에서 받은 백엔드 URL + `/api`
     - 예: `https://your-app.railway.app/api`
   - **Environments**: Production, Preview, Development 모두 체크

4. 환경 변수 추가 후 재배포:
   ```bash
   vercel --prod
   ```

### 배포 확인
- 메인 도메인: `https://loldabang.vercel.app`
- 브라우저 개발자 도구 (F12) → Network 탭에서 API 호출 확인
- CORS 오류나 404 오류가 없어야 함

---

## 로컬 개발 환경

### 백엔드 실행

1. **Python 가상 환경 생성 (선택사항)**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

3. **백엔드 실행**
   ```bash
   python main.py
   ```
   
   백엔드가 `http://localhost:4000`에서 실행됩니다.

### 프론트엔드 실행

1. **의존성 설치**
   ```bash
   cd frontend
   npm install
   ```

2. **환경 변수 설정 (선택사항)**
   
   `frontend/.env.local` 파일 생성:
   ```
   VITE_API_BASE_URL=http://localhost:4000/api
   ```

3. **개발 서버 실행**
   ```bash
   npm run dev
   ```
   
   프론트엔드가 `http://localhost:5173`에서 실행됩니다.

### 전체 스택 실행

루트 디렉토리에서:
```bash
# 백엔드 (터미널 1)
cd backend && python main.py

# 프론트엔드 (터미널 2)
cd frontend && npm run dev
```

---

## 문제 해결

### CORS 오류
**증상**: 브라우저 콘솔에 "Access-Control-Allow-Origin" 오류

**해결 방법**:
1. 백엔드 `main.py`에서 CORS 설정 확인:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_credentials=False,
       allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
       allow_headers=["*"],
   )
   ```
2. Railway에 재배포

### 401 Unauthorized 오류
**증상**: API 호출 시 401 오류 발생

**원인**: 데이터베이스가 초기화되지 않았거나 경로가 잘못됨

**해결 방법**:
1. Railway 로그 확인:
   ```bash
   railway logs
   ```
2. 데이터베이스 경로가 `/data/loldabang.db`인지 확인
3. 볼륨이 `/data`에 마운트되어 있는지 확인

### 환경 변수가 적용되지 않음
**증상**: 프론트엔드가 여전히 잘못된 API URL 사용

**해결 방법**:
1. Vercel 환경 변수가 올바르게 설정되었는지 확인
2. 환경 변수 변경 후 반드시 재배포:
   ```bash
   vercel --prod
   ```
3. 브라우저 캐시 클리어:
   - `Ctrl + F5` (하드 새로고침)
   - 또는 시크릿 모드에서 테스트

### Railway 데이터베이스가 초기화됨
**증상**: 서비스 재시작 후 데이터가 사라짐

**해결 방법**:
1. Railway 대시보드에서 볼륨이 올바르게 설정되었는지 확인
2. 볼륨 마운트 경로: `/data`
3. 백엔드 코드에서 `DB_PATH = "/data/loldabang.db"` 확인

### 빌드 실패
**증상**: Vercel 또는 Railway 빌드 중 오류 발생

**해결 방법**:
1. **프론트엔드**:
   ```bash
   cd frontend
   npm install
   npm run build
   ```
   로컬에서 빌드가 성공하는지 확인

2. **백엔드**:
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```
   로컬에서 실행이 성공하는지 확인

---

## 추가 리소스

- [Railway 문서](https://docs.railway.app)
- [Vercel 문서](https://vercel.com/docs)
- [FastAPI 문서](https://fastapi.tiangolo.com)
- [Vue.js 문서](https://vuejs.org)

---

## 지원

문제가 계속되면 다음을 확인하세요:
1. Railway 서비스 로그
2. Vercel 배포 로그
3. 브라우저 개발자 도구 콘솔
4. 네트워크 탭에서 API 요청/응답 확인
