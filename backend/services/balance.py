from typing import Optional, List, Tuple
import itertools

TIER_BASE = {
    "IRON": 0, "BRONZE": 200, "SILVER": 400, "GOLD": 600, "PLATINUM": 800,
    "EMERALD": 1000, "DIAMOND": 1200, "MASTER": 1500, "GRANDMASTER": 1700, "CHALLENGER": 1900,
}
DIV_ADDER = {"IV": 0, "III": 50, "II": 100, "I": 150}

def rank_to_score(tier: Optional[str], rank: Optional[str], lp: int) -> int:
    if not tier: return 0
    t = tier.upper()
    base = TIER_BASE.get(t, 0)
    if t in ("MASTER", "GRANDMASTER", "CHALLENGER"):
        return base + max(0, min(lp, 300))
    return base + DIV_ADDER.get((rank or "IV").upper(), 0) + max(0, min(lp, 100))

def blend_score(rank_score: int, winrate: Optional[float]) -> float:
    win_bonus = 0.0 if winrate is None else (winrate - 0.50) * 400  # 10%p ~= 40점
    return rank_score * 0.7 + win_bonus * 0.3

def best_split_5v5(scores: List[float]) -> Tuple[List[int], List[int], float]:
    idxs = list(range(10)); best = None; best_diff = 1e9
    for team_a in itertools.combinations(idxs, 5):
        if 0 not in team_a: continue  # mirror 제거
        team_b = [i for i in idxs if i not in team_a]
        a = sum(scores[i] for i in team_a); b = sum(scores[i] for i in team_b)
        diff = abs(a - b)
        if diff < best_diff: best_diff, best = diff, (list(team_a), team_b)
    return best[0], best[1], best_diff
