from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ..services.riot_client import (
    get_account_by_riot_id, get_summoner_by_puuid, get_league_entries,
    get_recent_match_ids, get_match
)
from ..services.balance import rank_to_score, blend_score, best_split_5v5

router = APIRouter(prefix="/api/riot", tags=["riot"])

class PlayerIn(BaseModel):
    gameName: str
    tagLine: str
    platform: str = "KR"

class TeamBalanceRequest(BaseModel):
    players: List[PlayerIn]
    recent: int = 8

class PlayerOut(BaseModel):
    gameName: str
    tagLine: str
    tier: Optional[str]
    rank: Optional[str]
    lp: int
    winrate: Optional[float]
    score: float

class TeamBalanceResponse(BaseModel):
    teamA: List[PlayerOut]
    teamB: List[PlayerOut]
    diff: float

@router.post("/balance-5v5", response_model=TeamBalanceResponse)
def balance_5v5(payload: TeamBalanceRequest):
    if len(payload.players) != 10:
        raise HTTPException(status_code=400, detail="players must be exactly 10.")

    computed: List[PlayerOut] = []
    for p in payload.players:
        acc = get_account_by_riot_id(p.platform, p.gameName, p.tagLine)
        summ = get_summoner_by_puuid(p.platform, acc["puuid"])
        leagues = get_league_entries(p.platform, summ["id"])
        solo = next((e for e in leagues if e.get("queueType")=="RANKED_SOLO_5x5"), None) or {}
        tier = solo.get("tier"); rank = solo.get("rank"); lp = int(solo.get("leaguePoints", 0))

        # recent winrate (weighted: 70% solo, 30% flex)
        try:
            ids = get_recent_match_ids(p.platform, summ["puuid"], payload.recent)
            solo_wins = solo_total = 0
            flex_wins = flex_total = 0
            for mid in ids:
                m = get_match(p.platform, mid)
                info = m.get("info", {})
                queue_id = info.get("queueId")
                me = next((pp for pp in info.get("participants", []) if pp.get("puuid")==summ["puuid"]), None)
                if not me:
                    continue
                if queue_id == 420:  # Ranked Solo
                    solo_total += 1
                    if me.get("win"):
                        solo_wins += 1
                elif queue_id == 440:  # Ranked Flex
                    flex_total += 1
                    if me.get("win"):
                        flex_wins += 1

            solo_wr = None if solo_total == 0 else solo_wins / solo_total
            flex_wr = None if flex_total == 0 else flex_wins / flex_total

            if solo_wr is None and flex_wr is None:
                wr = None
            elif solo_wr is None:
                wr = flex_wr
            elif flex_wr is None:
                wr = solo_wr
            else:
                wr = solo_wr * 0.7 + flex_wr * 0.3
        except Exception:
            wr = None

        rscore = rank_to_score(tier, rank, lp)
        score = blend_score(rscore, wr)

        computed.append(PlayerOut(
            gameName=p.gameName, tagLine=p.tagLine,
            tier=tier, rank=rank, lp=lp, winrate=wr, score=score
        ))

    scores = [c.score for c in computed]
    a_idx, b_idx, diff = best_split_5v5(scores)
    teamA = [computed[i] for i in a_idx]
    teamB = [computed[i] for i in b_idx]
    return TeamBalanceResponse(teamA=teamA, teamB=teamB, diff=diff)
