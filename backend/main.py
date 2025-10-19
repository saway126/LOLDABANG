from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional
try:
    import pysqlite3 as sqlite3
except ImportError:
    import sqlite3
import json
import re
from datetime import datetime
import uvicorn
import os
import asyncio
from riot_api import riot_api, RiotAPIService
from routers import riot_balance, riot_account_proxy

app = FastAPI(title="LoL Custom Match Tool API", version="1.0.0")

# 라이엇 API 서비스 인스턴스
riot_service = RiotAPIService()

# WebSocket 연결 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.admin_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, is_admin: bool = False):
        await websocket.accept()
        if is_admin:
            self.admin_connections.append(websocket)
        else:
            self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket, is_admin: bool = False):
        if is_admin:
            if websocket in self.admin_connections:
                self.admin_connections.remove(websocket)
        else:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            pass

    async def broadcast_to_admins(self, message: str):
        for connection in self.admin_connections:
            try:
                await connection.send_text(message)
            except:
                self.admin_connections.remove(connection)

    async def broadcast_to_all(self, message: str):
        for connection in self.active_connections + self.admin_connections:
            try:
                await connection.send_text(message)
            except:
                if connection in self.active_connections:
                    self.active_connections.remove(connection)
                if connection in self.admin_connections:
                    self.admin_connections.remove(connection)

manager = ConnectionManager()

# 데이터베이스 파일 경로 설정
# Railway 환경 감지 (여러 방법으로 확인)
is_railway = (
    os.environ.get('RAILWAY_ENVIRONMENT') or 
    os.environ.get('RAILWAY_PROJECT_ID') or
    os.environ.get('PORT')  # Railway는 항상 PORT 환경변수를 설정
)

if is_railway:
    # Railway 환경: 영구 볼륨 사용
    DB_PATH = "/data/loldabang.db"
    # /data 디렉토리가 없으면 생성
    try:
        os.makedirs("/data", exist_ok=True)
        print(f"Railway 환경 감지됨. DB 경로: {DB_PATH}")
    except Exception as e:
        print(f"Railway /data 디렉토리 생성 실패: {e}")
        # 대안으로 현재 디렉토리 사용
        DB_PATH = os.path.join(os.path.dirname(__file__), "loldabang.db")
        print(f"대안 DB 경로 사용: {DB_PATH}")
else:
    # 로컬 개발 환경
    DB_PATH = os.path.join(os.path.dirname(__file__), "loldabang.db")
    print(f"로컬 환경. DB 경로: {DB_PATH}")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용
    allow_credentials=False,  # credentials가 true면 allow_origins에 "*" 사용 불가
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)



def init_db():
    try:
        print(f"데이터베이스 초기화 시작 - 경로: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 테이블 생성 (IF NOT EXISTS 사용)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                tier TEXT,
                rank TEXT,
                mainLane TEXT,
                preferredLanes TEXT,
                mmr INTEGER,
                createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customId TEXT NOT NULL UNIQUE,
                host TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('soft', 'hard', 'hyper')),
                status TEXT DEFAULT 'open',
                createdAt DATETIME DEFAULT (datetime('now', '+9 hours'))
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS participants (
                matchId INTEGER NOT NULL,
                playerId INTEGER NOT NULL,
                status TEXT DEFAULT 'waiting',
                FOREIGN KEY (matchId) REFERENCES matches(id),
                FOREIGN KEY (playerId) REFERENCES players(id),
                PRIMARY KEY (matchId, playerId)
            )
        """)
        
        conn.commit()
        conn.close()
        print("데이터베이스 초기화 완료")
    except Exception as e:
        print(f"데이터베이스 초기화 실패: {e}")
        # Railway에서 데이터베이스 초기화 실패 시에도 앱이 시작되도록 함

# 데이터베이스 즉시 초기화
init_db()

# 헬스체크 엔드포인트
@app.get("/")
async def root():
    return {"message": "LoL Custom Match Tool API", "status": "running"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": "Railway" if is_railway else "Local",
        "database_path": DB_PATH,
        "port": os.environ.get("PORT", "4000")
    }

# Pydantic 모델들
class Player(BaseModel):
    name: str
    tier: str
    rank: str
    mainLane: str
    preferredLanes: List[str]

class MatchCreate(BaseModel):
    customId: str
    host: str
    type: str
    participants: List[Player]

class MatchResponse(BaseModel):
    id: int
    customId: str
    host: str
    type: str
    status: str
    createdAt: str
    participantCount: int

# 카카오톡 파싱 함수
def parse_kakao_talk(text: str) -> dict:
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    players = []
    errors = []

    for line in lines:
        try:
            normalized = line.replace('\s+', ' ')
            
            # 닉네임 매칭 (공백 허용)
            name_match = re.match(r'^([^#]+#[^\s]+)', normalized)
            if not name_match:
                raise ValueError(f"Invalid name format: {line}")
            
            name = name_match.group(1)
            remaining = normalized[len(name):].strip()
            
            # 티어 패턴 매칭
            tier_pattern = r'^([A-Za-z]+)(\d*)\s*/\s*([A-Za-z]+)(\d*)|^([A-Za-z]+)(\d*)|^/\s*([A-Za-z]+)(\d*)\s*/\s*([A-Za-z]+)(\d*)|^([A-Za-z]+)(\d*)\s*/\s*([A-Za-z]+)(\d*)'
            tier_match = re.match(tier_pattern, remaining)
            
            if not tier_match:
                tier = 'UNRANKED'
                rank = ''
            else:
                if tier_match.group(1) and tier_match.group(2):
                    tier = tier_match.group(1).upper()
                    rank = tier_match.group(2)
                elif tier_match.group(5) and tier_match.group(6):
                    tier = tier_match.group(5).upper()
                    rank = tier_match.group(6)
                elif tier_match.group(7) and tier_match.group(8):
                    tier = tier_match.group(7).upper()
                    rank = tier_match.group(8)
                elif tier_match.group(9) and tier_match.group(10):
                    tier = tier_match.group(9).upper()
                    rank = tier_match.group(10)
                else:
                    tier = 'UNRANKED'
                    rank = ''
            
            after_tier = re.sub(tier_pattern, '', remaining).strip()
            
            # 라인 매칭
            lane_match = None
            main_lane = 'UNKNOWN'
            preferred_lanes = []
            
            # 다양한 라인 패턴 매칭
            patterns = [
                r'^\s*([가-힣ㅇ-ㅎㄱ-ㅎA-Za-z]+)\s*/\s*(.+)',
                r'^\s*/\s*([가-힣ㅇ-ㅎㄱ-ㅎA-Za-z]+)\s*/\s*(.+)',
                r'^\s*([가-힣ㅇ-ㅎㄱ-ㅎA-Za-z]+)',
                r'\s+([가-힣ㅇ-ㅎㄱ-ㅎA-Za-z]+)'
            ]
            
            for pattern in patterns:
                lane_match = re.match(pattern, after_tier)
                if lane_match:
                    if len(lane_match.groups()) >= 2:
                        main_lane = lane_match.group(1).strip()
                        preferred_lanes = [l.strip() for l in lane_match.group(2).split() if l.strip() and l not in ['/', '-']]
                    else:
                        main_lane = lane_match.group(1).strip()
                        preferred_lanes = []
                    break
            
            # 라인 매핑
            lane_mapping = {
                'ㅇㄷ': 'ADC',
                'ㅅㅍ': 'SUPPORT',
                'ㅁㄷ': 'MID',
                'ㅈㄱ': 'JUNGLE',
                'ㅌ': 'TOP',
                'ㅁㄷㅇㄷ': 'MID ADC',
                '탑': 'TOP',
                '정글': 'JUNGLE',
                '미드': 'MID',
                '원딜': 'ADC',
                '서폿': 'SUPPORT',
                '정글서폿': 'JUNGLE SUPPORT',
                '정글탑': 'JUNGLE TOP',
                '미드탑': 'MID TOP',
                '원딜서폿': 'ADC SUPPORT',
                '서폿원딜': 'SUPPORT ADC'
            }
            
            main_lane = lane_mapping.get(main_lane, main_lane.upper())
            
            final_preferred_lanes = []
            for lane in preferred_lanes:
                if '정글서폿' in lane:
                    final_preferred_lanes.append('JUNGLE SUPPORT')
                elif '정글탑' in lane:
                    final_preferred_lanes.append('JUNGLE TOP')
                elif '미드탑' in lane:
                    final_preferred_lanes.append('MID TOP')
                elif '원딜서폿' in lane:
                    final_preferred_lanes.append('ADC SUPPORT')
                elif 'ㅁㄷㅇㄷ' in lane:
                    final_preferred_lanes.append('MID ADC')
                else:
                    final_preferred_lanes.append(lane_mapping.get(lane, lane.upper()))
            
            players.append(Player(
                name=name,
                tier=tier,
                rank=rank,
                mainLane=main_lane,
                preferredLanes=final_preferred_lanes
            ))
            
        except Exception as e:
            print(f"Parsing failed for line: {line}, Error: {e}")
            errors.append(line)
    
    return {"players": players, "errors": errors}

# API 엔드포인트들
@app.get("/api/health")
async def health_check():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.close()
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": "failed", "error": str(e)}

@app.get("/")
async def root():
    return {"message": "LoL Custom Match Tool API"}

@app.post("/api/parse")
async def parse_kakao_talk_endpoint(request: dict):
    text = request.get("text", "")
    result = parse_kakao_talk(text)
    return result

@app.post("/api/matches")
async def create_match(match_data: MatchCreate):
    print(f"Received match data: {match_data}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 매치 생성 (한국 시간 사용)
        cursor.execute(
            "INSERT INTO matches (customId, host, type, createdAt) VALUES (?, ?, ?, datetime('now', '+9 hours'))",
            (match_data.customId, match_data.host, match_data.type)
        )
        match_id = cursor.lastrowid
        
        # 플레이어 처리
        for player_data in match_data.participants:
            # 플레이어 존재 확인
            cursor.execute("SELECT id FROM players WHERE name = ?", (player_data.name,))
            player = cursor.fetchone()
            
            if not player:
                # 새 플레이어 생성
                cursor.execute(
                    "INSERT INTO players (name, tier, rank, mainLane, preferredLanes) VALUES (?, ?, ?, ?, ?)",
                    (player_data.name, player_data.tier, player_data.rank, player_data.mainLane, json.dumps(player_data.preferredLanes))
                )
                player_id = cursor.lastrowid
            else:
                # 기존 플레이어 업데이트
                player_id = player[0]
                cursor.execute(
                    "UPDATE players SET tier = ?, rank = ?, mainLane = ?, preferredLanes = ? WHERE id = ?",
                    (player_data.tier, player_data.rank, player_data.mainLane, json.dumps(player_data.preferredLanes), player_id)
                )
            
            # 참가자 추가
            cursor.execute(
                "INSERT OR IGNORE INTO participants (matchId, playerId) VALUES (?, ?)",
                (match_id, player_id)
            )
        
        conn.commit()
        return {"id": match_id, "customId": match_data.customId, "host": match_data.host, "type": match_data.type}
        
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=409, detail=f"Match with ID '{match_data.customId}' already exists.")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        conn.close()

@app.get("/api/matches/recent")
async def get_recent_matches():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT m.id, m.customId, m.host, m.type, m.status, m.createdAt,
                   COUNT(p.playerId) as participantCount
            FROM matches m
            LEFT JOIN participants p ON m.id = p.matchId
            GROUP BY m.id, m.customId, m.host, m.type, m.status, m.createdAt
            ORDER BY m.createdAt DESC
            LIMIT 10
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [MatchResponse(
            id=row[0],
            customId=row[1],
            host=row[2],
            type=row[3],
            status=row[4],
            createdAt=row[5],
            participantCount=row[6]
        ) for row in rows]
    except Exception as e:
        print(f"Database error in get_recent_matches: {e}")
        return []

@app.get("/api/matches/by-type/{match_type}")
async def get_matches_by_type(match_type: str):
    if match_type not in ['soft', 'hard', 'hyper']:
        raise HTTPException(status_code=400, detail="Invalid match type")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT m.id, m.customId, m.host, m.type, m.status, m.createdAt,
                   COUNT(p.playerId) as participantCount
            FROM matches m
            LEFT JOIN participants p ON m.id = p.matchId
            WHERE m.type = ?
            GROUP BY m.id, m.customId, m.host, m.type, m.status, m.createdAt
            ORDER BY m.createdAt DESC
        """, (match_type,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [MatchResponse(
            id=row[0],
            customId=row[1],
            host=row[2],
            type=row[3],
            status=row[4],
            createdAt=row[5],
            participantCount=row[6]
        ) for row in rows]
    except Exception as e:
        print(f"Database error in get_matches_by_type: {e}")
        return []

@app.get("/api/matches/{match_id}/participants")
async def get_match_participants(match_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.id, p.name, p.tier, p.rank, p.mainLane, p.preferredLanes
        FROM players p
        JOIN participants pa ON p.id = pa.playerId
        WHERE pa.matchId = ?
    """, (match_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    participants = []
    for row in rows:
        participants.append({
            "id": row[0],
            "name": row[1],
            "tier": row[2],
            "rank": row[3],
            "mainLane": row[4],
            "preferredLanes": json.loads(row[5]) if row[5] else []
        })
    
    return participants

@app.get("/api/matches/all")
async def get_all_matches():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, customId, host, type, status, createdAt, updatedAt
        FROM matches 
        ORDER BY createdAt DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    matches = []
    for row in rows:
        # 참가자 수 조회
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM participants WHERE matchId = ?", (row[0],))
        participant_count = cursor.fetchone()[0]
        conn.close()
        
        matches.append({
            "id": row[0],
            "customId": row[1],
            "host": row[2],
            "type": row[3],
            "status": row[4],
            "createdAt": row[5],
            "updatedAt": row[6],
            "participantCount": participant_count
        })
    
    return matches

@app.get("/api/matches/{match_id}")
async def get_match(match_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, customId, host, type, status, createdAt, updatedAt
        FROM matches 
        WHERE id = ?
    """, (match_id,))
    
    match_row = cursor.fetchone()
    if not match_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Match not found")
    
    # 참가자 수 조회
    cursor.execute("SELECT COUNT(*) FROM participants WHERE matchId = ?", (match_id,))
    participant_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "id": match_row[0],
        "customId": match_row[1],
        "host": match_row[2],
        "type": match_row[3],
        "status": match_row[4],
        "createdAt": match_row[5],
        "updatedAt": match_row[6],
        "participantCount": participant_count
    }

@app.put("/api/matches/{match_id}")
async def update_match(match_id: int, match_data: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 내전 정보 업데이트
        cursor.execute("""
            UPDATE matches 
            SET customId = ?, host = ?, type = ?, updatedAt = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (match_data['customId'], match_data['host'], match_data['type'], match_id))
        
        # 기존 참가자 삭제
        cursor.execute("DELETE FROM participants WHERE matchId = ?", (match_id,))
        
        # 새로운 참가자 추가
        for participant in match_data.get('participants', []):
            # 플레이어가 이미 존재하는지 확인
            cursor.execute("SELECT id FROM players WHERE name = ?", (participant['name'],))
            player_row = cursor.fetchone()
            
            if player_row:
                player_id = player_row[0]
            else:
                # 새 플레이어 생성
                cursor.execute("""
                    INSERT INTO players (name, tier, rank, mainLane, preferredLanes)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    participant['name'],
                    participant.get('tier', ''),
                    participant.get('rank', ''),
                    participant.get('mainLane', ''),
                    json.dumps(participant.get('preferredLanes', []))
                ))
                player_id = cursor.lastrowid
            
            # 참가자 관계 추가
            cursor.execute("""
                INSERT INTO participants (matchId, playerId)
                VALUES (?, ?)
            """, (match_id, player_id))
        
        conn.commit()
        return {"message": "내전이 성공적으로 수정되었습니다."}
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.delete("/api/matches/{match_id}")
async def delete_match(match_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 참가자 관계 삭제
        cursor.execute("DELETE FROM participants WHERE matchId = ?", (match_id,))
        
        # 내전 삭제
        cursor.execute("DELETE FROM matches WHERE id = ?", (match_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="내전을 찾을 수 없습니다.")
        
        conn.commit()
        return {"message": "내전이 성공적으로 삭제되었습니다."}
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ===== 라이엇 API 엔드포인트 =====

@app.get("/api/riot/player/{game_name}/{tag_line}")
async def get_player_info(game_name: str, tag_line: str):
    """라이엇 ID로 플레이어 정보 조회"""
    try:
        player_info = await riot_api.get_player_full_info(game_name, tag_line)
        if not player_info:
            raise HTTPException(status_code=404, detail="플레이어를 찾을 수 없습니다.")
        return player_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/riot/player/{game_name}/{tag_line}/league")
async def get_player_league(game_name: str, tag_line: str):
    """플레이어의 리그 정보 조회"""
    try:
        player_info = await riot_api.get_player_full_info(game_name, tag_line)
        if not player_info:
            raise HTTPException(status_code=404, detail="플레이어를 찾을 수 없습니다.")
        return {"league": player_info.get("league")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/riot/player/{game_name}/{tag_line}/champions")
async def get_player_champions(game_name: str, tag_line: str):
    """플레이어의 챔피언 마스터리 조회"""
    try:
        player_info = await riot_api.get_player_full_info(game_name, tag_line)
        if not player_info:
            raise HTTPException(status_code=404, detail="플레이어를 찾을 수 없습니다.")
        return {"champion_masteries": player_info.get("champion_masteries", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/riot/champion/{champion_id}")
async def get_champion_info(champion_id: int):
    """챔피언 정보 조회"""
    try:
        champion_info = await riot_api.get_champion_data(champion_id)
        if not champion_info:
            raise HTTPException(status_code=404, detail="챔피언을 찾을 수 없습니다.")
        return champion_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== WebSocket 실시간 통신 =====

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 클라이언트로부터 메시지 수신 처리
            message = json.loads(data)
            if message.get("type") == "ping":
                await manager.send_personal_message(json.dumps({"type": "pong"}), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/admin")
async def websocket_admin_endpoint(websocket: WebSocket):
    await manager.connect(websocket, is_admin=True)
    try:
        while True:
            data = await websocket.receive_text()
            # 관리자 메시지 처리
            message = json.loads(data)
            if message.get("type") == "ping":
                await manager.send_personal_message(json.dumps({"type": "pong"}), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, is_admin=True)

# ===== 실시간 내전 상태 관리 =====

@app.get("/api/matches/realtime")
async def get_realtime_matches():
    """실시간 내전 상태 조회"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 활성 내전 조회 (최근 1시간 내)
        cursor.execute("""
            SELECT id, customId, host, type, status, createdAt, updatedAt
            FROM matches 
            WHERE status = 'open' 
            AND datetime(createdAt) > datetime('now', '-1 hour', '+9 hours')
            ORDER BY createdAt DESC
        """)
        
        rows = cursor.fetchall()
        matches = []
        
        for row in rows:
            # 참가자 수 조회
            cursor.execute("SELECT COUNT(*) FROM participants WHERE matchId = ?", (row[0],))
            participant_count = cursor.fetchone()[0]
            
            matches.append({
                "id": row[0],
                "customId": row[1],
                "host": row[2],
                "type": row[3],
                "status": row[4],
                "createdAt": row[5],
                "updatedAt": row[6],
                "participantCount": participant_count,
                "isRealtime": True
            })
        
        return {
            "matches": matches,
            "totalCount": len(matches),
            "lastUpdated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.put("/api/matches/{match_id}/status")
async def update_match_status(match_id: str, status_data: dict):
    """내전 상태 업데이트 (실시간 관리용) - customId 또는 id 지원"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        new_status = status_data.get('status')
        if new_status not in ['open', 'closed', 'in_progress', 'completed']:
            raise HTTPException(status_code=400, detail="유효하지 않은 상태입니다.")
        
        # customId 또는 id로 내전 찾기
        if match_id.isdigit():
            # 숫자 ID인 경우
            cursor.execute("SELECT id, customId, host, type, status FROM matches WHERE id = ?", (int(match_id),))
        else:
            # customId인 경우
            cursor.execute("SELECT id, customId, host, type, status FROM matches WHERE customId = ?", (match_id,))
        
        match_info = cursor.fetchone()
        
        if not match_info:
            raise HTTPException(status_code=404, detail="내전을 찾을 수 없습니다.")
        
        actual_id = match_info[0]  # 실제 데이터베이스 ID
        
        cursor.execute("""
            UPDATE matches 
            SET status = ?, updatedAt = datetime('now', '+9 hours')
            WHERE id = ?
        """, (new_status, actual_id))
        
        conn.commit()
        
        # 실시간 알림 전송
        notification = {
            "type": "match_status_update",
            "match_id": actual_id,
            "custom_id": match_info[1],
            "host": match_info[2],
            "match_type": match_info[3],
            "old_status": match_info[4],
            "new_status": new_status,
            "timestamp": datetime.now().isoformat()
        }
        
        await manager.broadcast_to_all(json.dumps(notification))
        
        return {"message": f"내전 상태가 {new_status}로 업데이트되었습니다."}
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/api/matches/{match_id}/notify")
async def send_match_notification(match_id: int, notification_data: dict):
    """내전 알림 전송 (관리자용)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT customId, host, type FROM matches WHERE id = ?", (match_id,))
        match_info = cursor.fetchone()
        
        if not match_info:
            raise HTTPException(status_code=404, detail="내전을 찾을 수 없습니다.")
        
        notification = {
            "type": "admin_notification",
            "match_id": match_id,
            "custom_id": match_info[0],
            "host": match_info[1],
            "match_type": match_info[2],
            "message": notification_data.get('message', ''),
            "priority": notification_data.get('priority', 'normal'),
            "timestamp": datetime.now().isoformat()
        }
        
        await manager.broadcast_to_all(json.dumps(notification))
        
        return {"message": "알림이 전송되었습니다."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Vercel 핸들러
handler = app

# 라이엇 밸런싱 라우터 포함
app.include_router(riot_balance.router)
app.include_router(riot_account_proxy.router)

if __name__ == "__main__":
    try:
        # Railway 환경에서는 PORT 환경변수 사용, 없으면 4000 사용
        port = int(os.environ.get("PORT", 4000))
        print(f"서버 시작 - 포트: {port}, 환경: {'Railway' if is_railway else '로컬'}")
        print(f"데이터베이스 경로: {DB_PATH}")
        
        # Railway에서 앱 시작 전 최종 확인
        if is_railway:
            print("Railway 환경에서 서버 시작 중...")
            # 데이터베이스 파일 존재 확인
            if not os.path.exists(DB_PATH):
                print(f"데이터베이스 파일이 없습니다. 새로 생성합니다: {DB_PATH}")
                init_db()
        
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"서버 시작 실패: {e}")
        # Railway에서 크래시 방지를 위해 기본 설정으로 재시도
        print("기본 설정으로 재시도...")
        uvicorn.run(app, host="0.0.0.0", port=8000)

# 라이엇 API 엔드포인트
@app.get("/api/riot/summoner/{game_name}/{tag_line}")
async def get_summoner_by_riot_id(game_name: str, tag_line: str):
    """라이엇 ID로 소환사 정보 조회"""
    try:
        # 라이엇 API 키 확인
        if not riot_service.api_key:
            return {"success": False, "message": "라이엇 API 키가 설정되지 않았습니다. 관리자에게 문의하세요."}
        
        result = await riot_service.get_summoner_by_riot_id(game_name, tag_line)
        if result:
            return {"success": True, "data": result}
        else:
            return {"success": False, "message": "소환사를 찾을 수 없습니다."}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/api/riot/summoner/puuid/{puuid}")
async def get_summoner_by_puuid(puuid: str):
    """PUUID로 소환사 상세 정보 조회"""
    try:
        result = await riot_service.get_summoner_by_puuid(puuid)
        if result:
            return {"success": True, "data": result}
        else:
            return {"success": False, "message": "소환사를 찾을 수 없습니다."}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/api/riot/league/{summoner_id}")
async def get_summoner_league(summoner_id: str):
    """소환사 리그 정보 조회"""
    try:
        result = await riot_service.get_summoner_league(summoner_id)
        if result:
            return {"success": True, "data": result}
        else:
            return {"success": False, "message": "리그 정보를 찾을 수 없습니다."}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/api/riot/champion-mastery/{summoner_id}")
async def get_champion_mastery(summoner_id: str):
    """소환사 챔피언 숙련도 조회"""
    try:
        result = await riot_service.get_champion_mastery(summoner_id)
        if result:
            return {"success": True, "data": result}
        else:
            return {"success": False, "message": "챔피언 숙련도 정보를 찾을 수 없습니다."}
    except Exception as e:
        return {"success": False, "message": str(e)}
