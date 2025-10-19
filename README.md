# LoL 내전 도구 (loldabang)

리그 오브 레전드 내부전을 위한 팀 밸런싱 도구입니다. 웹과 모바일에서 모두 사용할 수 있습니다.

## 🚀 주요 기능

- **내전 종류 보기** 🎮: 소프트/하드/하이퍼 피어리스 설명 및 종류별 내전 목록
- **내전 생성** ➕: 카카오톡 댓글 파싱을 통한 참가자 등록
- **밸런스 조율** ⚖️: 참가자 선택, 팀 밸런싱, 팀장 선택
- **실시간 내전 관리** 🔄: WebSocket 기반 실시간 내전 상태 업데이트
- **밴픽 관리** 🎯: 실시간 밴픽 진행 상황 추적
- **라이엇 API 연동** 🔍: 소환사 정보 자동 조회 및 캐싱
- **알림 시스템** 🔔: 실시간 알림 및 브라우저 알림 지원

## 🛠 기술 스택

- **프론트엔드**: Vue.js 3 + TypeScript + Vite + Tailwind CSS
- **백엔드**: Python FastAPI + SQLite3 + WebSocket
- **외부 API**: Riot Games API (선택적)
- **배포**: Railway (백엔드) + Vercel (프론트엔드)
- **플랫폼**: 웹 (모바일 반응형 지원)

## 📱 설치 및 실행

### 1. 의존성 설치
```bash
# 프론트엔드 의존성
npm install

# 백엔드 의존성
cd backend
pip install -r requirements.txt
```

### 2. 개발 서버 실행
```bash
# 백엔드 서버 실행 (포트 4000)
python backend/main.py

# 프론트엔드 실행 (포트 5173)
npm run dev -w frontend
```

### 3. 브라우저에서 접속
```
http://localhost:5173
```

## 🎯 사용법

### 내전 생성
1. **내전 생성** 탭 선택
2. 내전 ID, 진행자, 종류 입력
3. 카카오톡 댓글 형식으로 참가자 정보 입력:
   ```
   닉네임#태그 티어랭크 주라인 / 희망라인1 희망라인2
   ```
   예시:
   ```
   홍길동#KR1 G1 TOP / JUNGLE MID
   김철수#KR2 S2 JUNGLE / TOP
   이영희#KR3 P4 MID / ADC
   ```
4. "파싱" 버튼으로 참가자 목록 생성
5. 원하는 참가자 선택 후 "내전 생성"

### 내전 종류별 조회
1. **내전 종류** 탭에서 원하는 종류 클릭
2. 해당 종류의 내전 목록 확인
3. 각 내전의 상세 정보 (호스트, 참가자 수, 생성일) 확인

### 밸런스 조율
1. **밸런스 조율** 탭 선택
2. 최근 내전 선택
3. 참가자 선택 (최소 10명)
4. "밸런싱 실행"으로 팀 구성
5. 팀장 선택 및 품질 점수 확인
6. **라이엇 API 연동**: 소환사명#태그 형식으로 등록된 플레이어의 라이엇 데이터 자동 조회

### 실시간 내전 관리
1. **실시간** 탭에서 활성 내전 목록 확인
2. 내전 상태 실시간 업데이트 (WebSocket 또는 폴링)
3. 내전 시작/종료 상태 변경
4. 실시간 알림으로 상태 변화 추적

### 밴픽 관리
1. **밴픽** 탭에서 밴픽 진행 중인 내전 확인
2. 실시간 밴픽 상황 추적
3. 팀 구성 및 밴픽 순서 관리

## 📊 API 명세

### 루트
- `GET /` - API 상태 확인

### 카카오톡 파싱
- `POST /api/parse`
- 요청: `{ text: string }`
- 응답: `{ players: Player[], errors: string[] }`

### 내전 관리
- `POST /api/matches` - 내전 생성
- `GET /api/matches/recent` - 최근 내전 조회
- `GET /api/matches/by-type/{type}` - 종류별 내전 조회
- `GET /api/matches/{id}/participants` - 참가자 조회
- `PUT /api/matches/{id}/status` - 내전 상태 업데이트

### 실시간 기능
- `WebSocket /ws` - 실시간 내전 상태 업데이트
- `GET /api/matches/active` - 활성 내전 조회

### 라이엇 API 연동 (선택적)
- `GET /api/riot/summoner/{game_name}/{tag_line}` - 라이엇 ID로 소환사 정보 조회
- `GET /api/riot/summoner/puuid/{puuid}` - PUUID로 소환사 상세 정보 조회
- `GET /api/riot/league/{summoner_id}` - 소환사 리그 정보 조회
- `GET /api/riot/champion-mastery/{summoner_id}` - 챔피언 숙련도 조회

## 🎮 카카오톡 댓글 파싱 형식

### 기본 형식
```
닉네임#태그 티어랭크 주라인 / 희망라인1 희망라인2
```

### 지원하는 티어
- **영문**: IRON, BRONZE, SILVER, GOLD, PLATINUM, EMERALD, DIAMOND, MASTER, GRANDMASTER, CHALLENGER
- **약어**: I, B, S, G, P, E, D, M, GM, C
- **숫자**: 1-4 (랭크)

### 지원하는 라인
- **한글**: 탑, 정글, 미드, 원딜, 서폿
- **영문**: TOP, JUNGLE, MID, ADC, SUPPORT
- **자모**: ㅌ, ㅈㄱ, ㅁㄷ, ㅇㄷ, ㅅㅍ
- **복합**: 정글서폿, 미드탑, 원딜서폿 등

### 파싱 예시
```
레몬#9999 P2/P2 탑/탑 미드
단면도#kr1 E3/P4 서폿/서폿원딜
유나라#정인 D4/E3 ㅇㄷ/ㅁㄷ ㅇㄷ ㅌ
킹크스#no1 G3/G1 원딜 / 미드 원딜
```

## 🏗 프로젝트 구조

```
loldabang/
├── frontend/              # Vue.js 프론트엔드
│   ├── src/
│   │   ├── views/         # 페이지 컴포넌트
│   │   │   ├── Home.vue   # 내전 종류 및 목록
│   │   │   ├── Create.vue # 내전 생성
│   │   │   └── Balance.vue # 팀 밸런싱
│   │   ├── router/        # 라우팅 설정
│   │   └── main.ts        # 앱 진입점
│   ├── package.json
│   └── vite.config.ts
├── backend/               # Python FastAPI 백엔드
│   ├── main.py           # FastAPI 애플리케이션
│   ├── requirements.txt  # Python 의존성
│   └── loldabang.db      # SQLite 데이터베이스
├── shared/               # 공용 타입 및 유틸리티
│   ├── types.ts          # TypeScript 타입 정의
│   └── utils/            # 유틸리티 함수
├── package.json          # 루트 패키지 설정
└── README.md
```

## 🎨 주요 특징

### 고급 카카오톡 파싱
- 한국어 자모 지원 (ㅇㄷ, ㅅㅍ, ㅁㄷ, ㅈㄱ, ㅌ)
- 복합 라인명 파싱 (정글서폿, 미드탑, 원딜서폿)
- 유연한 티어 형식 (P1/P1, E4/E4, m240/d2)
- 공백이 포함된 닉네임 지원

### 스마트 팀 밸런싱
- 그리디 알고리즘 기반 팀 구성
- 티어 기반 점수 시스템 (Iron 1점 ~ Challenger 10점)
- 라인 선호도 고려
- 팀장 선택 기능
- 시각적 품질 점수 표시

### 현대적인 UI/UX
- Vue.js 3 + TypeScript + Vite
- Tailwind CSS로 반응형 디자인
- 티어별 색상 코딩
- 라인 아이콘 및 시각적 표시
- 로딩 상태 및 에러 처리

## 🔧 개발 명령어

```bash
# 전체 개발 서버 실행
npm run dev

# 프론트엔드만 실행
npm run dev -w frontend

# 백엔드만 실행
python backend/main.py

# 프로덕션 빌드
npm run build
```

## 📱 플랫폼 지원

- **웹**: Chrome, Firefox, Safari, Edge
- **모바일**: 반응형 디자인으로 모바일 브라우저 지원

## 🎉 완성된 기능

✅ **프론트엔드**
- Vue.js 3 + TypeScript + Vite 설정
- 반응형 디자인 (웹/모바일)
- 내전 종류별 목록 조회
- 카카오톡 댓글 파싱 UI
- 팀 밸런싱 및 팀장 선택
- 실시간 내전 관리 인터페이스
- 밴픽 관리 시스템
- 라이엇 API 연동 UI
- 실시간 알림 시스템

✅ **백엔드**
- Python FastAPI 서버
- SQLite 데이터베이스
- RESTful API 엔드포인트
- WebSocket 실시간 통신
- 고급 카카오톡 파싱 로직
- 라이엇 API 연동 서비스
- CORS 및 에러 처리

✅ **데이터베이스**
- 매치, 플레이어, 참가자 테이블
- JSON 기반 희망라인 저장
- 자동 스키마 생성

✅ **실시간 기능**
- WebSocket 기반 실시간 업데이트
- 폴링 폴백 메커니즘
- 실시간 알림 시스템
- 브라우저 알림 지원

✅ **라이엇 API 연동**
- 소환사 정보 자동 조회
- 리그 정보 및 챔피언 숙련도 조회
- 로컬 캐싱 시스템
- API 키 설정 안내

## 🚀 빠른 시작

1. **저장소 클론**
   ```bash
   git clone https://github.com/saway126/LOLDABANG.git
   cd LOLDABANG
   ```

2. **의존성 설치**
   ```bash
   npm install
   cd backend && pip install -r requirements.txt && cd ..
   ```

3. **서버 실행**
   ```bash
   # 백엔드 (터미널 1)
   python backend/main.py
   
   # 프론트엔드 (터미널 2)
   npm run dev -w frontend
   ```

4. **브라우저 접속**
   ```
   http://localhost:5173
   ```

## 🌐 배포

자세한 배포 가이드는 [DEPLOYMENT.md](./DEPLOYMENT.md)를 참고하세요.

### 빠른 배포 가이드

**백엔드 (Railway)**
1. Railway 계정 생성 및 GitHub 연동
2. Railway 대시보드에서 `backend` 디렉토리 배포
3. `/data` 경로에 영구 볼륨 마운트
4. 도메인 생성 및 URL 복사

**프론트엔드 (Vercel)**
1. Vercel 대시보드에서 환경 변수 설정:
   - `VITE_API_BASE_URL`: Railway 백엔드 URL + `/api`
2. 프론트엔드 빌드 및 배포:
   ```bash
   cd frontend && npm run build
   vercel --prod
   ```

**라이엇 API 설정 (선택적)**
1. [Riot Games Developer Portal](https://developer.riotgames.com/)에서 API 키 발급
2. Railway 대시보드에서 환경 변수 설정:
   - `RIOT_API_KEY`: 발급받은 라이엇 API 키
3. 재배포 후 라이엇 API 기능 활성화

## 🌐 배포 URL

- **프론트엔드**: https://loldabang.vercel.app
- **백엔드**: https://loldabang-production.up.railway.app

## 📄 라이선스

ISC

---

**개발자**: saway126  
**GitHub**: [https://github.com/saway126/LOLDABANG](https://github.com/saway126/LOLDABANG)