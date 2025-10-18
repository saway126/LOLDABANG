# ===== 내전 관리 시스템 클래스 =====

class MatchManager:
    def __init__(self, riot_api: RiotAPIManager):
        """
        내전 관리자 초기화
        
        Args:
            riot_api (RiotAPIManager): 라이엇 API 매니저 인스턴스
        """
        self.riot_api = riot_api
        self.matches = []  # 내전 목록
        self.players = {}  # 플레이어 정보 캐시
        
    def add_player(self, game_name: str, tag_line: str) -> Optional[Dict]:
        """플레이어 추가"""
        player_key = f"{game_name}#{tag_line}"
        
        if player_key in self.players:
            print(f"✅ 플레이어 정보 캐시에서 로드: {player_key}")
            return self.players[player_key]
        
        print(f"🔍 플레이어 정보 조회 중: {player_key}")
        player_info = self.riot_api.get_player_full_info(game_name, tag_line)
        
        if player_info:
            self.players[player_key] = player_info
            print(f"✅ 플레이어 추가 완료: {player_key}")
            return player_info
        else:
            print(f"❌ 플레이어 추가 실패: {player_key}")
            return None
    
    def create_match(self, match_id: str, match_type: str, host: str, players: List[str]) -> Dict:
        """내전 생성"""
        match_data = {
            'id': match_id,
            'type': match_type,
            'host': host,
            'players': [],
            'status': 'open',
            'created_at': datetime.now().isoformat(),
            'blue_team': [],
            'red_team': [],
            'bans': [],
            'picks': []
        }
        
        # 플레이어 정보 수집
        for player in players:
            if '#' in player:
                game_name, tag_line = player.split('#', 1)
                player_info = self.add_player(game_name, tag_line)
                if player_info:
                    match_data['players'].append(player_info)
        
        self.matches.append(match_data)
        print(f"✅ 내전 생성 완료: {match_id} ({len(match_data['players'])}명 참가)")
        return match_data
    
    def get_match(self, match_id: str) -> Optional[Dict]:
        """내전 조회"""
        for match in self.matches:
            if match['id'] == match_id:
                return match
        return None
    
    def update_match_status(self, match_id: str, status: str) -> bool:
        """내전 상태 업데이트"""
        match = self.get_match(match_id)
        if match:
            match['status'] = status
            match['updated_at'] = datetime.now().isoformat()
            print(f"✅ 내전 상태 업데이트: {match_id} -> {status}")
            return True
        return False
    
    def analyze_team_balance(self, match_id: str) -> Dict:
        """팀 밸런스 분석"""
        match = self.get_match(match_id)
        if not match:
            return {}
        
        # 티어별 점수 매핑
        tier_scores = {
            'IRON': 1, 'BRONZE': 2, 'SILVER': 3, 'GOLD': 4,
            'PLATINUM': 5, 'DIAMOND': 6, 'MASTER': 7, 'GRANDMASTER': 8, 'CHALLENGER': 9
        }
        
        rank_scores = {'IV': 0.25, 'III': 0.5, 'II': 0.75, 'I': 1.0}
        
        def calculate_player_score(player):
            if not player.get('league'):
                return 0
            
            league = player['league']
            tier = league.get('tier', 'IRON')
            rank = league.get('rank', 'IV')
            lp = league.get('leaguePoints', 0)
            
            base_score = tier_scores.get(tier, 1)
            rank_multiplier = rank_scores.get(rank, 0.5)
            lp_bonus = lp / 1000  # LP를 소수점으로 변환
            
            return base_score + rank_multiplier + lp_bonus
        
        # 플레이어 점수 계산
        player_scores = [calculate_player_score(player) for player in match['players']]
        
        # 팀 분배 (간단한 알고리즘)
        sorted_players = sorted(zip(match['players'], player_scores), key=lambda x: x[1], reverse=True)
        
        blue_team = []
        red_team = []
        
        for i, (player, score) in enumerate(sorted_players):
            if i % 2 == 0:
                blue_team.append((player, score))
            else:
                red_team.append((player, score))
        
        blue_score = sum(score for _, score in blue_team)
        red_score = sum(score for _, score in red_team)
        
        balance_analysis = {
            'blue_team': blue_team,
            'red_team': red_team,
            'blue_score': blue_score,
            'red_score': red_score,
            'balance_ratio': min(blue_score, red_score) / max(blue_score, red_score) if max(blue_score, red_score) > 0 else 0,
            'is_balanced': abs(blue_score - red_score) < 1.0
        }
        
        return balance_analysis
    
    def get_match_statistics(self) -> Dict:
        """내전 통계 조회"""
        total_matches = len(self.matches)
        active_matches = len([m for m in self.matches if m['status'] == 'open'])
        completed_matches = len([m for m in self.matches if m['status'] == 'completed'])
        total_players = len(self.players)
        
        # 티어 분포
        tier_distribution = {}
        for player in self.players.values():
            if player.get('league'):
                tier = player['league'].get('tier', 'UNRANKED')
                tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
        
        return {
            'total_matches': total_matches,
            'active_matches': active_matches,
            'completed_matches': completed_matches,
            'total_players': total_players,
            'tier_distribution': tier_distribution,
            'last_updated': datetime.now().isoformat()
        }

print("✅ MatchManager 클래스 정의 완료!")
