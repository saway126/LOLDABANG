# 롤다방 배포 가이드

## 🚀 프로덕션 URL
**메인 URL**: https://loldabang.vercel.app

## 📋 배포 파이프라인 구성

### 1. Vercel 프로젝트 설정
- **프로젝트 ID**: `prj_yAXNseQ7XT3WtidLAzCVJAFssZTF`
- **프로젝트명**: `loldabang`
- **도메인**: `loldabang.vercel.app`

### 2. 환경 변수 설정
다음 환경 변수들이 Vercel에 설정되어 있습니다:
- `VITE_API_URL`: `https://loldabang-production.up.railway.app/api`
- `VITE_WS_URL`: `wss://loldabang-production.up.railway.app/ws`

### 3. 자동 배포 설정

#### GitHub Actions 설정
1. GitHub 저장소의 Settings > Secrets and variables > Actions에서 다음 시크릿을 추가:
   - `VERCEL_TOKEN`: Vercel 계정 토큰
   - `VERCEL_ORG_ID`: Vercel 조직 ID

2. `main` 브랜치에 푸시하면 자동으로 배포됩니다.

#### 수동 배포
```bash
# Vercel CLI를 사용한 수동 배포
vercel --prod

# 또는 npm 스크립트 사용
npm run build
```

### 4. 빌드 프로세스

#### 로컬 빌드
```bash
# 프론트엔드 빌드
cd frontend
npm install
npm run build

# 빌드 결과를 public 폴더로 복사
cp -r dist/* ../public/
```

#### Vercel 빌드
- **빌드 명령어**: `npm run vercel-build`
- **출력 디렉토리**: `public`
- **프레임워크**: Vite

### 5. 파일 구조
```
loldabang/
├── frontend/          # Vue.js 프론트엔드
├── backend/           # FastAPI 백엔드 (Railway 배포)
├── public/            # 빌드된 정적 파일 (Vercel 배포)
├── vercel.json        # Vercel 설정
├── .github/workflows/ # GitHub Actions
└── package.json       # 루트 패키지 설정
```

## 🔧 개발 환경 설정

### 로컬 개발 서버 실행
```bash
# 프론트엔드 개발 서버
cd frontend
npm install
npm run dev

# 백엔드 개발 서버
cd backend
pip install -r requirements.txt
python main.py
```

### 환경 변수 설정
프론트엔드 개발 시 `frontend/.env.local` 파일 생성:
```
VITE_API_URL=http://localhost:4000/api
VITE_WS_URL=ws://localhost:4000/ws
```

## 📊 모니터링

### Vercel 대시보드
- [Vercel 프로젝트](https://vercel.com/skwka12346-gmailcoms-projects/loldabang)
- 배포 상태, 로그, 성능 메트릭 확인 가능

### Railway 대시보드
- [Railway 프로젝트](https://railway.app/project/loldabang-production)
- 백엔드 API 상태 및 로그 확인 가능

## 🚨 문제 해결

### 배포 실패 시
1. Vercel 로그 확인: `vercel logs [deployment-url]`
2. GitHub Actions 로그 확인
3. 로컬 빌드 테스트: `npm run vercel-build`

### 환경 변수 문제
1. Vercel 대시보드에서 환경 변수 확인
2. `vercel env ls` 명령어로 확인
3. 필요시 `vercel env add` 명령어로 추가

### WebSocket 연결 문제
1. Railway 백엔드 상태 확인
2. CORS 설정 확인
3. 방화벽/프록시 설정 확인

## 📝 배포 체크리스트

- [ ] 코드 변경사항 커밋 및 푸시
- [ ] GitHub Actions 워크플로우 실행 확인
- [ ] Vercel 배포 상태 확인
- [ ] 프로덕션 URL 접속 테스트
- [ ] 실시간 기능 동작 확인
- [ ] API 연결 상태 확인

## 🔗 관련 링크

- **프로덕션 사이트**: https://loldabang.vercel.app
- **Vercel 대시보드**: https://vercel.com/skwka12346-gmailcoms-projects/loldabang
- **Railway 대시보드**: https://railway.app/project/loldabang-production
- **GitHub 저장소**: https://github.com/[username]/loldabang
