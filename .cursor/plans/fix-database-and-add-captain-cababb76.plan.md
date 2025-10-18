<!-- cababb76-7805-43bb-8904-2b97220d294b 82f3ace6-39d6-47ae-af25-7c6222131661 -->
# loldabang.vercel.app 배포 및 에러 수정 계획

## 1. 사용하지 않는 코드 정리

### 1.1 useWebSocket import 제거
**파일**: `frontend/src/views/RealtimeBalance.vue`
- 337번째 줄: `import { useWebSocket } from '../composables/useWebSocket'` 삭제

**파일**: `frontend/src/components/RealtimeNotification.vue`
- 104번째 줄: `import { useWebSocket } from '../composables/useWebSocket'` 삭제

## 2. 환경 변수 통일 및 설정

### 2.1 환경 변수명 통일
현재 혼재된 환경 변수명 통일:
- `VITE_API_BASE_URL` → `VITE_API_URL`로 변경
- `VITE_WS_URL` 유지

**수정 대상 파일들**:
- `frontend/src/views/Home.vue` (211번 줄)
- `frontend/src/views/Create.vue` (164번 줄)
- `frontend/src/views/MatchDetail.vue` (110번 줄)
- `frontend/src/views/Balance.vue` (190번 줄)
- `frontend/src/vite-env.d.ts` (4번 줄)

변경 내용:
```typescript
// 변경 전
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 

// 변경 후
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://loldabang-production.up.railway.app/api'
```

### 2.2 환경 변수 파일 생성
**파일**: `frontend/.env.production`
```
VITE_API_URL=https://loldabang-production.up.railway.app/api
VITE_WS_URL=wss://loldabang-production.up.railway.app/ws
```

**파일**: `frontend/.env.local` (개발용)
```
VITE_API_URL=http://localhost:4000/api
VITE_WS_URL=ws://localhost:4000/ws
```

## 3. Vercel 배포 설정

### 3.1 vercel.json 생성
**파일**: `frontend/vercel.json`
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### 3.2 Vercel 환경 변수 설정
Vercel 대시보드에서 설정해야 할 환경 변수:
- `VITE_API_URL` = `https://loldabang-production.up.railway.app/api`
- `VITE_WS_URL` = `wss://loldabang-production.up.railway.app/ws`

### 3.3 루트 vercel.json 삭제
**파일**: `vercel.json` (루트)
- 삭제 (frontend 폴더를 직접 배포하므로 불필요)

## 4. 배포 실행

### 4.1 Frontend 빌드 테스트
```bash
cd frontend
npm run build
```

### 4.2 Vercel 배포
```bash
cd frontend
npx vercel --prod
```

### 4.3 도메인 연결 확인
- Vercel 대시보드에서 `loldabang.vercel.app` 도메인이 제대로 연결되었는지 확인
- 기존 프로젝트 업데이트 방식 사용

## 5. 배포 후 검증

### 5.1 기능 테스트
- 홈페이지 접속: `https://loldabang.vercel.app`
- API 연결 확인: 내전 목록 로드 테스트
- 라우팅 확인: `/realtime`, `/realtime-balance`, `/banpick` 등

### 5.2 콘솔 에러 확인
- WebSocket 연결 실패 경고만 있고 치명적 오류 없는지 확인
- 404 에러 없는지 확인

## 필요한 Vercel 환경 변수 정리

1. **VITE_API_URL**: 백엔드 API 기본 URL
   - Production: `https://loldabang-production.up.railway.app/api`

2. **VITE_WS_URL**: WebSocket URL
   - Production: `wss://loldabang-production.up.railway.app/ws`


### To-dos

- [ ] Railway 설정 파일 및 런타임 파일 생성
- [ ] 백엔드 데이터베이스 경로를 Railway 영구 볼륨으로 수정
- [ ] 프론트엔드에서 환경 변수로 API URL 사용하도록 수정
- [ ] Railway CLI로 백엔드 배포 및 URL 확인
- [ ] Vercel 환경 변수 설정 (VITE_API_BASE_URL)
- [ ] 프론트엔드 재빌드 및 Vercel 재배포
- [ ] 백엔드-프론트엔드 연결 테스트
- [ ] 배포 문서 업데이트