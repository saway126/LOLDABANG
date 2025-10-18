# Railway 백엔드 배포 가이드

## 🚀 Railway 배포 단계별 가이드

### 1단계: Railway 계정 준비

1. [Railway](https://railway.app) 접속
2. GitHub 계정으로 로그인
3. Railway와 GitHub 연동 확인

### 2단계: 프로젝트 생성

1. Railway 대시보드에서 **"New Project"** 클릭
2. **"Deploy from GitHub repo"** 선택
3. 저장소 선택 (loldabang)
4. **중요**: Root Directory를 `backend`로 설정
5. **"Deploy"** 클릭

### 3단계: 영구 볼륨 설정

1. 배포된 서비스 클릭
2. **"Variables"** 탭 클릭
3. **"New Volume"** 클릭
4. **Mount Path**: `/data` 입력
5. **"Add"** 클릭
6. 서비스 재시작 (자동)

### 4단계: 도메인 생성

1. **"Settings"** 탭 클릭
2. **"Public Networking"** 섹션 찾기
3. **"Generate Domain"** 클릭
4. 생성된 URL 복사 (예: `https://your-app.railway.app`)

### 5단계: 헬스체크

브라우저에서 다음 URL 접속:
```
https://your-app.railway.app/api/health
```

예상 응답:
```json
{
  "status": "ok",
  "database": "connected"
}
```

### 6단계: Vercel 환경 변수 설정

1. [Vercel 대시보드](https://vercel.com/dashboard) 접속
2. 프로젝트 선택
3. **"Settings"** → **"Environment Variables"**
4. 새 환경 변수 추가:
   - **Name**: `VITE_API_BASE_URL`
   - **Value**: `https://your-app.railway.app/api`
   - **Environments**: Production, Preview, Development 모두 체크
5. **"Save"** 클릭

### 7단계: 프론트엔드 재배포

```bash
# 로컬에서 실행
vercel --prod
```

### 8단계: 최종 테스트

1. Vercel 프론트엔드 URL 접속
2. 브라우저 개발자 도구 (F12) 열기
3. Network 탭에서 API 호출 확인
4. CORS 오류나 404 오류가 없는지 확인

## 🔧 문제 해결

### 배포 실패
- Railway 로그 확인: 서비스 → "Deployments" → 로그 보기
- Python 버전 확인: `runtime.txt`에 `python-3.11.6` 설정됨
- 의존성 확인: `requirements.txt` 파일 존재

### 데이터베이스 오류
- 영구 볼륨이 `/data`에 마운트되었는지 확인
- 서비스 재시작 후 다시 시도

### CORS 오류
- 백엔드가 정상 배포되었는지 확인
- 프론트엔드에서 올바른 API URL 사용하는지 확인

### 404 오류
- Vercel 환경 변수 `VITE_API_BASE_URL`이 올바르게 설정되었는지 확인
- 프론트엔드 재배포 후 브라우저 캐시 클리어

## 📞 지원

문제가 계속되면:
1. Railway 서비스 로그 확인
2. Vercel 배포 로그 확인
3. 브라우저 개발자 도구 콘솔 확인
4. 네트워크 탭에서 API 요청/응답 확인
