from fastapi import APIRouter, HTTPException, Query
import os, requests

router = APIRouter(prefix="/api/riot/account", tags=["riot"])
RIOT_TOKEN = os.getenv("RIOT_API_KEY")
ASIA = "https://asia.api.riotgames.com"

@router.get("/by-riot-id")
def by_riot_id(gameName: str = Query(...), tagLine: str = Query(...)):
    if not RIOT_TOKEN:
        raise HTTPException(500, "RIOT_API_KEY missing")
    url = f"{ASIA}/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
    r = requests.get(url, headers={"X-Riot-Token": RIOT_TOKEN}, timeout=10)
    if r.status_code != 200:
        raise HTTPException(r.status_code, r.text)
    data = r.json()
    # 최소한의 필드만 리턴
    return { "gameName": data.get("gameName"), "tagLine": data.get("tagLine"), "puuid": data.get("puuid") }
