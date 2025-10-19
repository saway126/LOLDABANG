import os, time, requests
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")

PLATFORM_BASE = {
    "KR": "https://kr.api.riotgames.com",
    "NA1": "https://na1.api.riotgames.com",
    "EUW1": "https://euw1.api.riotgames.com",
    "EUN1": "https://eun1.api.riotgames.com",
    "JP1": "https://jp1.api.riotgames.com",
    "OC1": "https://oc1.api.riotgames.com",
    "BR1": "https://br1.api.riotgames.com",
    "LA1": "https://la1.api.riotgames.com",
    "LA2": "https://la2.api.riotgames.com",
    "TR1": "https://tr1.api.riotgames.com",
    "RU": "https://ru.api.riotgames.com",
}

REGION_BASE = {
    "ASIA": "https://asia.api.riotgames.com",
    "AMERICAS": "https://americas.api.riotgames.com",
    "EUROPE": "https://europe.api.riotgames.com",
}

PLATFORM_TO_REGION = {
    "KR": "ASIA", "JP1": "ASIA", "OC1": "ASIA",
    "NA1": "AMERICAS", "BR1": "AMERICAS", "LA1": "AMERICAS", "LA2": "AMERICAS",
    "EUW1": "EUROPE", "EUN1": "EUROPE", "TR1": "EUROPE", "RU": "EUROPE",
}

def _riot_get(url: str, params: Optional[dict] = None, retries: int = 3):
    if not RIOT_API_KEY:
        raise RuntimeError("RIOT_API_KEY is not set")
    headers = {"X-Riot-Token": RIOT_API_KEY}
    for attempt in range(retries):
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code == 429:
            wait = int(r.headers.get("Retry-After", "2"))
            time.sleep(wait); continue
        if 200 <= r.status_code < 300:
            return r.json()
        if r.status_code >= 500 and attempt < retries - 1:
            time.sleep(1.5 * (attempt + 1)); continue
        raise RuntimeError(f"Riot API error {r.status_code}: {r.text}")
    raise RuntimeError("Riot API retries exhausted")

def get_account_by_riot_id(platform: str, game_name: str, tag_line: str) -> Dict:
    region = PLATFORM_TO_REGION.get(platform, "ASIA")
    url = f"{REGION_BASE[region]}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    return _riot_get(url)

def get_summoner_by_puuid(platform: str, puuid: str) -> Dict:
    url = f"{PLATFORM_BASE[platform]}/lol/summoner/v4/summoners/by-puuid/{puuid}"
    return _riot_get(url)

def get_league_entries(platform: str, summoner_id: str) -> list:
    url = f"{PLATFORM_BASE[platform]}/lol/league/v4/entries/by-summoner/{summoner_id}"
    return _riot_get(url)

def get_recent_match_ids(platform: str, puuid: str, count: int = 8) -> List[str]:
    region = PLATFORM_TO_REGION.get(platform, "ASIA")
    url = f"{REGION_BASE[region]}/lol/match/v5/matches/by-puuid/{puuid}/ids"
    return _riot_get(url, params={"start": 0, "count": count})

def get_match(platform: str, match_id: str) -> dict:
    region = PLATFORM_TO_REGION.get(platform, "ASIA")
    url = f"{REGION_BASE[region]}/lol/match/v5/matches/{match_id}"
    return _riot_get(url)
