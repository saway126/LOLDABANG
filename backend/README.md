# 롤다방 내전프로그램 백엔드

FastAPI 기반의 백엔드 서버입니다.

## 🚀 Railway 배포

### 자동 배포 (GitHub 연동)

1. [Railway 대시보드](https://railway.app/dashboard) 접속
2. "New Project" → "Deploy from GitHub repo" 선택
3. 저장소 선택 후 **Root Directory를 `backend`로 설정**
4. 배포 완료 후 도메인 생성
5. 영구 볼륨 설정 (Mount Path: `/data`)

### 수동 배포 (Railway CLI)

```bash
# Railway CLI 설치
npm install -g @railway/cli

# 로그인
railway login

# 프로젝트 초기화
railway init

# 배포
railway up

# 도메인 생성
railway domain
```

## 🔧 로컬 개발

```bash
# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python main.py
```

서버가 `http://localhost:4000`에서 실행됩니다.

## 📊 API 엔드포인트

- `GET /` - API 상태 확인
- `GET /api/health` - 헬스체크
- `POST /api/parse` - 카카오톡 파싱
- `POST /api/matches` - 내전 생성
- `GET /api/matches/recent` - 최근 내전 조회
- `GET /api/matches/by-type/{type}` - 종류별 내전 조회
- `GET /api/matches/{id}/participants` - 참가자 조회

## 🗄️ 데이터베이스

- **개발 환경**: 로컬 SQLite 파일 (`loldabang.db`)
- **프로덕션 환경**: Railway 영구 볼륨 (`/data/loldabang.db`)

## 🌐 CORS 설정

모든 도메인에서 접근 가능하도록 설정되어 있습니다.

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```
