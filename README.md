# LoL 내전 도구 (loldabang)

리그 오브 레전드 내부전을 위한 팀 밸런싱 도구입니다. 웹과 모바일에서 모두 사용할 수 있습니다.

## 🚀 기능

- **내전 종류 보기** 🎮: 소프트/하드/하이퍼 피어리스 설명
- **내전 생성** ➕: 카톡 댓글 파싱을 통한 참가자 등록
- **밸런스 조율** ⚖️: 참가자 선택 및 팀 밸런싱

## 🛠 기술 스택

- **프론트엔드**: React Native + Expo (웹/모바일 호환)
- **백엔드**: Node.js + Express + TypeScript + SQLite3
- **플랫폼**: 웹, Android, iOS

## 📱 설치 및 실행

### 1. 의존성 설치
```bash
npm install
```

### 2. 백엔드 서버 실행
```bash
cd apps/server
npm run build
npm start
```
서버는 `http://localhost:4000`에서 실행됩니다.

### 3. 모바일/웹 앱 실행
```bash
cd apps/mobile_app
npm run web    # 웹에서 실행
npm run android # Android에서 실행
npm run ios    # iOS에서 실행 (macOS 필요)
```

### 4. 브라우저에서 접속
```
http://localhost:8081 (웹)
```

## 🎯 사용법

### 내전 생성
1. **내전 생성** 탭 선택
2. 내전 ID, 진행자, 종류 입력
3. 카톡 댓글 형식으로 참가자 정보 입력:
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

### 밸런스 조율
1. **밸런스 조율** 탭 선택
2. 최근 내전 선택
3. 참가자 선택 (최소 10명)
4. "밸런싱 실행"으로 팀 구성
5. 품질 점수와 팀 구성 결과 확인

## 📊 API 명세

### 내전 종류 조회
- `GET /api/types`
- 응답: 내전 종류 목록

### 카톡 댓글 파싱
- `POST /api/players/bulk-parse`
- 요청: `{ text: string }`
- 응답: `{ players: Player[], errors: string[] }`

### 내전 생성
- `POST /api/matches`
- 요청: `{ customId: string, host: string, type: string, participants: string[] }`
- 응답: `{ id: number, customId: string, host: string, type: string }`

### 최근 내전 조회
- `GET /api/matches/recent`
- 응답: 최근 5개 내전 목록

### 참가자 조회
- `GET /api/matches/:id/participants`
- 응답: 참가자 목록

### 팀 밸런싱
- `POST /api/balance`
- 요청: `{ players: Player[], options: { teamSize: number } }`
- 응답: `{ teams: Team[], qualityScore: number }`

## 🏗 프로젝트 구조

```
loldabang/
├── apps/
│   ├── server/          # Express API 서버 (포트 4000)
│   └── mobile_app/      # React Native + Expo 앱 (포트 8081)
├── shared/              # 공용 타입 및 유틸리티
└── README.md           # 프로젝트 문서
```

## 🎮 카톡 댓글 파싱 형식

```
닉네임#태그 티어랭크 주라인 / 희망라인1 희망라인2
```

**지원하는 티어:**
- IRON, BRONZE, SILVER, GOLD, PLATINUM, EMERALD, DIAMOND, MASTER, GRANDMASTER, CHALLENGER
- 약어: I, B, S, G, P, E, D, M, GM, C

**지원하는 라인:**
- TOP, JUNGLE, MID, ADC, SUPPORT

## 📱 플랫폼 지원

- **웹**: Chrome, Firefox, Safari, Edge
- **Android**: Android 6.0+ (API 23+)
- **iOS**: iOS 11.0+

## 🔧 개발 명령어

- `npm install`: 의존성 설치
- `npm run dev`: 개발 서버 실행 (서버: 4000포트, 앱: 8081포트)
- `npm run build`: 프로덕션 빌드

## 📄 라이선스

ISC

## 🎉 완성된 기능

✅ TypeScript 오류 수정  
✅ React Native + Expo로 웹/모바일 호환 앱 구현  
✅ 백엔드 API 서버 안정화  
✅ 카톡 댓글 파싱 기능  
✅ 팀 밸런싱 알고리즘  
✅ 반응형 UI/UX  
✅ 접근성 지원 (aria-label 등)  

**바로 실행 명령:**
1. `npm install`
2. `cd apps/server && npm run build && npm start` (백엔드)
3. `cd apps/mobile_app && npm run web` (프론트엔드)
4. `http://localhost:8081` 접속