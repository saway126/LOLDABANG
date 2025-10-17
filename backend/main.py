from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import json
import re
from datetime import datetime
import uvicorn

app = FastAPI(title="LoL Custom Match Tool API", version="1.0.0")

# 앱 시작 시 데이터베이스 초기화
@app.on_event("startup")
async def startup_event():
    init_db()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용
    allow_credentials=False,  # credentials가 true면 allow_origins에 "*" 사용 불가
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)



# 데이터베이스 초기화
def init_db():
    conn = sqlite3.connect('loldabang.db')
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
            createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
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
    print("Database initialized.")

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
    conn = sqlite3.connect('loldabang.db')
    cursor = conn.cursor()
    
    try:
        # 매치 생성
        cursor.execute(
            "INSERT INTO matches (customId, host, type) VALUES (?, ?, ?)",
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
        conn = sqlite3.connect('loldabang.db')
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
        conn = sqlite3.connect('loldabang.db')
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
    conn = sqlite3.connect('loldabang.db')
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

# Vercel 핸들러
handler = app

if __name__ == "__main__":
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=4000)
