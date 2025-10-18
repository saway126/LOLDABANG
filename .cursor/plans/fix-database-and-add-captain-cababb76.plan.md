<!-- cababb76-7805-43bb-8904-2b97220d294b 9a02a7a6-221c-4ffc-b786-43604bab4c7f -->
# 백엔드/프론트엔드 별도 배포 및 연결

## 1. 백엔드 Railway 배포 준비

### 1.1 Railway 설정 파일 생성

- `backend/railway.json` 생성
- 빌드 및 시작 명령 설정
- 환경 변수 설정

### 1.2 데이터베이스 경로 수정

- `backend/main.py`에서 `DB_PATH` 수정
- Railway 영구 볼륨(`/data/loldabang.db`) 사용
- 개발 환경에서는 로컬 경로 사용하도록 조건부 설정

### 1.3 런타임 파일 추가

- `backend/runtime.txt` 생성 (Python 버전 명시)
- `backend/Procfile` 생성 (Railway 시작 명령)

## 2. 프론트엔드 환경 변수 설정

### 2.1 프론트엔드 코드 수정

- `frontend/src/views/Home.vue`, `Create.vue`, `Balance.vue`에서 API URL을 환경 변수로 변경
- `import.meta.env.VITE_API_BASE_URL` 사용
- 개발 환경에서는 `http://localhost:4000/api` 기본값 설정

### 2.2 환경 변수 예시 파일

- `frontend/.env.example` 생성
- Vercel 환경 변수 설정 가이드 추가

## 3. Railway 배포 (수동 단계 필요)

### 3.1 Railway 대시보드에서 배포

Railway CLI는 비대화형 환경에서 로그인할 수 없으므로, Railway 대시보드를 통한 배포를 권장합니다:

1. https://railway.app/dashboard 접속
2. "New Project" → "Deploy from GitHub repo" 선택
3. 저장소 선택 및 `backend` 디렉토리 지정
4. 배포 완료 후 도메인 생성
5. 생성된 URL 복사 (예: https://your-app.railway.app)

### 3.2 영구 볼륨 설정

- Railway 프로젝트 대시보드에서 "Variables" 탭
- "New Volume" 클릭
- Mount Path: `/data`
- 저장 후 서비스 재시작

## 4. Vercel 프론트엔드 재배포

### 4.1 Vercel 환경 변수 설정

- Vercel 대시보드에서 `VITE_API_BASE_URL` 환경 변수 추가
- Railway에서 받은 백엔드 URL 입력

### 4.2 프론트엔드 재빌드 및 배포

- `frontend` 디렉토리에서 빌드
- `public` 폴더로 복사
- Vercel에 배포

## 5. 연결 테스트

### 5.1 백엔드 헬스체크

- Railway 백엔드 URL `/api/health` 접속 확인

### 5.2 프론트엔드-백엔드 연결 테스트

- Vercel 프론트엔드 접속
- 브라우저 개발자 도구에서 API 호출 확인
- CORS 오류 없이 데이터 로드 확인

## 6. 문서화

### 6.1 DEPLOYMENT.md 업데이트

- Railway 배포 가이드 추가
- Vercel 환경 변수 설정 가이드 업데이트
- 로컬 개발 환경 설정 가이드 추가

### To-dos

- [ ] Railway 설정 파일 및 런타임 파일 생성
- [ ] 백엔드 데이터베이스 경로를 Railway 영구 볼륨으로 수정
- [ ] 프론트엔드에서 환경 변수로 API URL 사용하도록 수정
- [ ] Railway CLI로 백엔드 배포 및 URL 확인
- [ ] Vercel 환경 변수 설정 (VITE_API_BASE_URL)
- [ ] 프론트엔드 재빌드 및 Vercel 재배포
- [ ] 백엔드-프론트엔드 연결 테스트
- [ ] 배포 문서 업데이트