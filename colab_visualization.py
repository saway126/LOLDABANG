# ===== 시각화 및 대시보드 클래스 =====

class MatchVisualizer:
    def __init__(self, match_manager: MatchManager):
        """
        내전 시각화 매니저 초기화
        
        Args:
            match_manager (MatchManager): 내전 관리자 인스턴스
        """
        self.match_manager = match_manager
    
    def plot_tier_distribution(self, figsize=(12, 8)):
        """티어 분포 시각화"""
        stats = self.match_manager.get_match_statistics()
        tier_dist = stats['tier_distribution']
        
        if not tier_dist:
            print("❌ 티어 분포 데이터가 없습니다.")
            return
        
        # 티어 순서 정의
        tier_order = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER']
        ordered_tiers = {tier: tier_dist.get(tier, 0) for tier in tier_order if tier in tier_dist}
        
        plt.figure(figsize=figsize)
        bars = plt.bar(ordered_tiers.keys(), ordered_tiers.values(), 
                      color=['#8B4513', '#CD7F32', '#C0C0C0', '#FFD700', '#00CED1', '#9932CC', '#FF69B4', '#FF4500', '#FF0000'])
        
        plt.title('플레이어 티어 분포', fontsize=16, fontweight='bold')
        plt.xlabel('티어', fontsize=12)
        plt.ylabel('플레이어 수', fontsize=12)
        plt.xticks(rotation=45)
        
        # 값 표시
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.show()
    
    def plot_team_balance(self, match_id: str, figsize=(12, 6)):
        """팀 밸런스 시각화"""
        balance = self.match_manager.analyze_team_balance(match_id)
        
        if not balance:
            print("❌ 팀 밸런스 데이터가 없습니다.")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # 팀 점수 비교
        teams = ['블루팀', '레드팀']
        scores = [balance['blue_score'], balance['red_score']]
        colors = ['#1f77b4', '#ff7f0e']
        
        bars = ax1.bar(teams, scores, color=colors)
        ax1.set_title('팀 밸런스 점수', fontsize=14, fontweight='bold')
        ax1.set_ylabel('점수', fontsize=12)
        
        # 값 표시
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.2f}', ha='center', va='bottom')
        
        # 밸런스 비율
        balance_ratio = balance['balance_ratio']
        ax2.pie([balance_ratio, 1-balance_ratio], 
                labels=['밸런스', '불균형'], 
                colors=['#2ecc71', '#e74c3c'],
                autopct='%1.1f%%')
        ax2.set_title(f'밸런스 비율: {balance_ratio:.2f}', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def plot_champion_mastery(self, player_name: str, figsize=(12, 6)):
        """챔피언 마스터리 시각화"""
        player_key = None
        for key, player in self.match_manager.players.items():
            if player['game_name'] == player_name:
                player_key = key
                break
        
        if not player_key:
            print(f"❌ 플레이어를 찾을 수 없습니다: {player_name}")
            return
        
        player = self.match_manager.players[player_key]
        masteries = player.get('champion_masteries', [])
        
        if not masteries:
            print(f"❌ {player_name}의 챔피언 마스터리 데이터가 없습니다.")
            return
        
        # 챔피언 이름과 마스터리 포인트 추출
        champion_names = []
        mastery_points = []
        
        for mastery in masteries:
            champion_id = mastery['championId']
            points = mastery['championPoints']
            champion_name = self.match_manager.riot_api.champions.get(champion_id, {}).get('name', f'Champion_{champion_id}')
            champion_names.append(champion_name)
            mastery_points.append(points)
        
        plt.figure(figsize=figsize)
        bars = plt.barh(champion_names, mastery_points, color='skyblue')
        
        plt.title(f'{player_name}의 챔피언 마스터리 TOP {len(champion_names)}', fontsize=16, fontweight='bold')
        plt.xlabel('마스터리 포인트', fontsize=12)
        plt.ylabel('챔피언', fontsize=12)
        
        # 값 표시
        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                    f'{mastery_points[i]:,}', ha='left', va='center')
        
        plt.tight_layout()
        plt.show()
    
    def create_dashboard(self):
        """대시보드 생성"""
        stats = self.match_manager.get_match_statistics()
        
        print("🎮 내전 관리 대시보드")
        print("=" * 50)
        print(f"📊 총 내전 수: {stats['total_matches']}")
        print(f"🔥 활성 내전: {stats['active_matches']}")
        print(f"✅ 완료된 내전: {stats['completed_matches']}")
        print(f"👥 등록된 플레이어: {stats['total_players']}")
        print(f"🕐 마지막 업데이트: {stats['last_updated']}")
        print("=" * 50)
        
        # 티어 분포 시각화
        if stats['tier_distribution']:
            print("\n📈 티어 분포:")
            self.plot_tier_distribution()
        
        # 활성 내전 목록
        active_matches = [m for m in self.match_manager.matches if m['status'] == 'open']
        if active_matches:
            print(f"\n🔥 활성 내전 목록 ({len(active_matches)}개):")
            for match in active_matches:
                print(f"  • {match['id']} ({match['type']}) - {len(match['players'])}명 참가")

print("✅ MatchVisualizer 클래스 정의 완료!")
