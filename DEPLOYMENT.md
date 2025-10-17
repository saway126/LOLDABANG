# 롤다방 내전프로그램 배포 가이드

## 🚀 Vercel 배포

### 현재 배포 상태
- **메인 도메인**: https://loldabang.vercel.app
- **프로젝트 ID**: `prj_yAXNseQ7XT3WtidLAzCVJAFssZTF`
- **팀 ID**: `skwka12346-gmailcoms-projects`

### GitHub Actions CI/CD 설정

#### 1. GitHub Secrets 설정
GitHub 저장소의 Settings > Secrets and variables > Actions에서 다음 secrets를 추가하세요:

```
VERCEL_TOKEN=your_vercel_token
VERCEL_ORG_ID=skwka12346-gmailcoms-projects
VERCEL_PROJECT_ID=prj_yAXNseQ7XT3WtidLAzCVJAFssZTF
```

#### 2. Vercel Token 생성
1. Vercel 대시보드 (https://vercel.com/account/tokens) 접속
2. "Create Token" 클릭
3. 토큰 이름 입력 (예: "GitHub Actions")
4. 생성된 토큰을 `VERCEL_TOKEN`으로 설정

#### 3. 자동 배포 활성화
- `main` 브랜치에 푸시할 때마다 자동으로 Vercel에 배포됩니다
- Pull Request 생성 시 테스트가 실행됩니다

## 🔧 로컬 개발

### 백엔드 실행
```bash
python backend/main.py
```

### 프론트엔드 실행
```bash
npm run dev -w frontend
```

### 전체 애플리케이션 실행
```bash
npm run dev
```

## 📁 프로젝트 구조

```
loldabang/
├── backend/                 # Python FastAPI 백엔드
│   ├── main.py
│   └── requirements.txt
├── frontend/               # Vue.js 프론트엔드
│   ├── src/
│   ├── public/
│   └── dist/
├── public/                 # Vercel 배포용 정적 파일
├── .github/workflows/      # GitHub Actions CI/CD
├── vercel.json            # Vercel 설정
└── package.json           # 루트 패키지 설정
```

## 🎨 주요 기능

- **홈페이지**: 내전 종류 선택 (소프트/하드/하이퍼 피어리스)
- **내전 생성**: 카카오톡 댓글 파싱으로 참가자 등록
- **밸런스 조율**: 팀 밸런싱 및 팀장 선택
- **반응형 디자인**: 모바일/데스크톱 최적화
- **이미지 통합**: 각 내전 종류별 고유 배경 이미지

## 🔄 배포 프로세스

1. 코드 변경 후 `main` 브랜치에 푸시
2. GitHub Actions가 자동으로 테스트 실행
3. 테스트 통과 시 Vercel에 자동 배포
4. 배포 완료 후 https://loldabang.vercel.app 에서 확인

## 🐛 문제 해결

### Vercel 로그인 페이지가 나타나는 경우
1. 브라우저 캐시 완전 삭제
2. 시크릿/프라이빗 모드에서 접속
3. 다른 브라우저에서 시도

### 빌드 실패 시
1. 로컬에서 `npm run build` 테스트
2. TypeScript 오류 확인
3. 의존성 문제 해결
