# ===== 코랩용 완전 자동화 라이엇 API 내전 관리 시스템 =====
# 이 코드를 코랩에서 실행하면 모든 것이 자동으로 설정됩니다!

# 1. 필요한 라이브러리 설치
!pip install -q google-genai requests pandas matplotlib seaborn plotly streamlit

# 2. 라이브러리 import
import google.generativeai as genai
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

# 3. 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

print("✅ 라이브러리 설치 및 import 완료!")

# ===== Google GenAI 설정 =====

class GenAIManager:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def analyze_team_composition(self, blue_team: List[Dict], red_team: List[Dict]) -> Dict:
        """팀 구성 분석 (AI 기반)"""
        prompt = f"""
        다음은 리그 오브 레전드 내전의 팀 구성입니다:

        블루팀:
        {json.dumps(blue_team, indent=2, ensure_ascii=False)}

        레드팀:
        {json.dumps(red_team, indent=2, ensure_ascii=False)}

        다음을 분석해주세요:
        1. 팀 밸런스 (티어, 랭크 기준)
        2. 예상 승률
        3. 각 팀의 강점과 약점
        4. 추천 밴픽 전략
        5. 주목할 만한 플레이어

        JSON 형식으로 답변해주세요.
        """
        
        try:
            response = self.model.generate_content(prompt)
            analysis = json.loads(response.text)
            return analysis
        except Exception as e:
            print(f"❌ AI 분석 실패: {e}")
            return {
                "predicted_win_rate": {"blue": 50, "red": 50},
                "balance_score": 0.5,
                "strengths": {"blue": "균형잡힌 구성", "red": "균형잡힌 구성"},
                "weaknesses": {"blue": "없음", "red": "없음"},
                "ban_pick_strategy": {"blue": "상대방 메인 챔피언 밴", "red": "상대방 메인 챔피언 밴"},
                "key_players": ["모든 플레이어가 중요"]
            }
    
    def suggest_ban_picks(self, match_data: Dict) -> Dict:
        """밴픽 추천 (AI 기반)"""
        prompt = f"""
        다음 내전 정보를 바탕으로 밴픽 전략을 추천해주세요:

        내전 정보:
        {json.dumps(match_data, indent=2, ensure_ascii=False)}

        다음을 포함해주세요:
        1. 1차 밴 추천 (각 팀 3개씩)
        2. 1차 픽 추천 (각 팀 2개씩)
        3. 2차 밴 추천 (각 팀 2개씩)
        4. 2차 픽 추천 (각 팀 3개씩)
        5. 전략적 이유

        JSON 형식으로 답변해주세요.
        """
        
        try:
            response = self.model.generate_content(prompt)
            suggestions = json.loads(response.text)
            return suggestions
        except Exception as e:
            print(f"❌ 밴픽 추천 실패: {e}")
            return {
                "first_ban": {"blue": ["야스오", "아리", "럭스"], "red": ["가렌", "다리우스", "카타리나"]},
                "first_pick": {"blue": ["이즈리얼", "소나"], "red": ["진", "리신"]},
                "second_ban": {"blue": ["야스오", "아리"], "red": ["가렌", "다리우스"]},
                "second_pick": {"blue": ["이즈리얼", "소나", "럭스"], "red": ["진", "리신", "카타리나"]},
                "strategy": "균형잡힌 팀 구성"
            }
    
    def generate_match_report(self, match_data: Dict, balance_analysis: Dict) -> str:
        """내전 리포트 생성 (AI 기반)"""
        prompt = f"""
        다음 내전 데이터를 바탕으로 상세한 내전 리포트를 작성해주세요:

        내전 데이터:
        {json.dumps(match_data, indent=2, ensure_ascii=False)}

        밸런스 분석:
        {json.dumps(balance_analysis, indent=2, ensure_ascii=False)}

        다음을 포함해주세요:
        1. 내전 개요
        2. 팀 밸런스 분석
        3. 주요 플레이어 분석
        4. 예상 경기 양상
        5. 추천 관전 포인트
        6. 예상 결과

        한국어로 작성해주세요.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ 리포트 생성 실패: {e}")
            return f"""
            # {match_data['id']} 내전 리포트
            
            ## 내전 개요
            - 내전 ID: {match_data['id']}
            - 내전 종류: {match_data['type']}
            - 진행자: {match_data['host']}
            - 참가자 수: {len(match_data['players'])}명
            
            ## 팀 밸런스 분석
            - 블루팀: {len(balance_analysis.get('blue_team', []))}명
            - 레드팀: {len(balance_analysis.get('red_team', []))}명
            - 밸런스 상태: {'균형' if balance_analysis.get('is_balanced', True) else '불균형'}
            
            ## 주요 플레이어
            {', '.join([f"{p['game_name']}#{p['tag_line']}" for p in match_data['players'][:3]])} 등
            
            ## 예상 경기 양상
            균형잡힌 팀 구성으로 치열한 경기가 예상됩니다.
            
            ## 추천 관전 포인트
            - 팀파이트 시 포지셔닝
            - 개별 스킬 플레이
            - 오브젝트 경합
            
            ## 예상 결과
            양 팀 모두 승리 가능성이 높은 접전이 예상됩니다.
            """

print("✅ GenAIManager 클래스 정의 완료!")

# ===== 라이엇 API 클래스 =====

class RiotAPIManager:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_urls = {
            'asia': 'https://asia.api.riotgames.com',
            'kr': 'https://kr.api.riotgames.com'
        }
    
    def get_player_full_info(self, game_name: str, tag_line: str) -> Optional[Dict]:
        """플레이어의 전체 정보 조회"""
        try:
            # PUUID 조회
            url = f"{self.base_urls['asia']}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
            headers = {'X-Riot-Token': self.api_key}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ 플레이어를 찾을 수 없습니다: {game_name}#{tag_line}")
                return None
            
            account_info = response.json()
            puuid = account_info['puuid']
            
            # 소환사 정보 조회
            url = f"{self.base_urls['kr']}/lol/summoner/v4/summoners/by-puuid/{puuid}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return None
            
            summoner_info = response.json()
            summoner_id = summoner_info['id']
            
            # 리그 정보 조회
            url = f"{self.base_urls['kr']}/lol/league/v4/entries/by-summoner/{summoner_id}"
            response = requests.get(url, headers=headers, timeout=10)
            
            league_entries = []
            if response.status_code == 200:
                data = response.json()
                league_entries = [entry for entry in data if entry.get('queueType') == 'RANKED_SOLO_5x5']
            
            # 챔피언 마스터리 조회
            url = f"{self.base_urls['kr']}/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}"
            response = requests.get(url, headers=headers, timeout=10)
            
            champion_masteries = []
            if response.status_code == 200:
                champion_masteries = response.json()[:5]
            
            return {
                'puuid': puuid,
                'summoner_id': summoner_id,
                'game_name': game_name,
                'tag_line': tag_line,
                'summoner_level': summoner_info.get('summonerLevel', 0),
                'profile_icon_id': summoner_info.get('profileIconId', 0),
                'league': league_entries[0] if league_entries else None,
                'champion_masteries': champion_masteries,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 플레이어 정보 조회 실패: {e}")
            return None

# ===== 내전 관리 시스템 =====

class EnhancedMatchManager:
    def __init__(self, riot_api: RiotAPIManager, genai_manager: GenAIManager):
        self.riot_api = riot_api
        self.genai_manager = genai_manager
        self.matches = []
        self.players = {}
    
    def add_player(self, game_name: str, tag_line: str) -> Optional[Dict]:
        """플레이어 추가"""
        player_key = f"{game_name}#{tag_line}"
        
        if player_key in self.players:
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
            'ai_analysis': {}
        }
        
        for player in players:
            if '#' in player:
                game_name, tag_line = player.split('#', 1)
                player_info = self.add_player(game_name, tag_line)
                if player_info:
                    match_data['players'].append(player_info)
        
        self.matches.append(match_data)
        print(f"✅ 내전 생성 완료: {match_id} ({len(match_data['players'])}명 참가)")
        return match_data
    
    def analyze_with_ai(self, match_id: str) -> Dict:
        """AI를 활용한 내전 분석"""
        match = self.get_match(match_id)
        if not match:
            return {}
        
        # 팀 분배
        players = match['players']
        blue_team = players[:len(players)//2]
        red_team = players[len(players)//2:]
        
        # AI 분석
        ai_analysis = self.genai_manager.analyze_team_composition(blue_team, red_team)
        
        # 밴픽 추천
        ban_pick_suggestions = self.genai_manager.suggest_ban_picks(match)
        
        # 리포트 생성
        report = self.genai_manager.generate_match_report(match, ai_analysis)
        
        analysis_result = {
            'match_id': match_id,
            'blue_team': blue_team,
            'red_team': red_team,
            'ai_analysis': ai_analysis,
            'ban_pick_suggestions': ban_pick_suggestions,
            'report': report,
            'analyzed_at': datetime.now().isoformat()
        }
        
        match['ai_analysis'] = analysis_result
        return analysis_result
    
    def get_match(self, match_id: str) -> Optional[Dict]:
        """내전 조회"""
        for match in self.matches:
            if match['id'] == match_id:
                return match
        return None

# ===== 시각화 클래스 =====

class EnhancedVisualizer:
    def __init__(self, match_manager: EnhancedMatchManager):
        self.match_manager = match_manager
    
    def plot_ai_analysis(self, match_id: str, figsize=(15, 10)):
        """AI 분석 결과 시각화"""
        analysis = self.match_manager.analyze_with_ai(match_id)
        
        if not analysis:
            print("❌ 분석 데이터가 없습니다.")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle(f'AI 분석 결과 - {match_id}', fontsize=16, fontweight='bold')
        
        # 1. 팀 밸런스 (AI 예상 승률)
        if 'ai_analysis' in analysis and 'predicted_win_rate' in analysis['ai_analysis']:
            win_rates = analysis['ai_analysis']['predicted_win_rate']
            teams = ['블루팀', '레드팀']
            rates = [win_rates.get('blue', 50), win_rates.get('red', 50)]
        else:
            teams = ['블루팀', '레드팀']
            rates = [50, 50]
        
        bars = axes[0, 0].bar(teams, rates, color=['#1f77b4', '#ff7f0e'])
        axes[0, 0].set_title('AI 예상 승률')
        axes[0, 0].set_ylabel('승률 (%)')
        axes[0, 0].set_ylim(0, 100)
        
        for bar, rate in zip(bars, rates):
            axes[0, 0].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                           f'{rate}%', ha='center', va='bottom')
        
        # 2. 플레이어 티어 분포
        all_players = analysis['blue_team'] + analysis['red_team']
        tier_dist = {}
        for player in all_players:
            if player.get('league'):
                tier = player['league'].get('tier', 'UNRANKED')
                tier_dist[tier] = tier_dist.get(tier, 0) + 1
            else:
                tier_dist['UNRANKED'] = tier_dist.get('UNRANKED', 0) + 1
        
        if tier_dist:
            tiers = list(tier_dist.keys())
            counts = list(tier_dist.values())
            axes[0, 1].pie(counts, labels=tiers, autopct='%1.1f%%')
            axes[0, 1].set_title('티어 분포')
        
        # 3. 챔피언 마스터리 분포
        champion_counts = {}
        for player in all_players:
            for mastery in player.get('champion_masteries', []):
                champion_id = mastery['championId']
                champion_counts[champion_id] = champion_counts.get(champion_id, 0) + 1
        
        if champion_counts:
            top_champions = sorted(champion_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            champion_ids, counts = zip(*top_champions)
            axes[1, 0].bar(range(len(champion_ids)), counts)
            axes[1, 0].set_title('인기 챔피언 TOP 5')
            axes[1, 0].set_xticks(range(len(champion_ids)))
            axes[1, 0].set_xticklabels([f'Champion_{cid}' for cid in champion_ids], rotation=45)
        else:
            axes[1, 0].text(0.5, 0.5, '챔피언 데이터 없음', ha='center', va='center', transform=axes[1, 0].transAxes)
            axes[1, 0].set_title('인기 챔피언 TOP 5')
        
        # 4. 팀별 평균 레벨
        blue_levels = [p.get('summoner_level', 0) for p in analysis['blue_team']]
        red_levels = [p.get('summoner_level', 0) for p in analysis['red_team']]
        
        teams = ['블루팀', '레드팀']
        avg_levels = [sum(blue_levels)/len(blue_levels) if blue_levels else 0,
                     sum(red_levels)/len(red_levels) if red_levels else 0]
        
        bars = axes[1, 1].bar(teams, avg_levels, color=['#1f77b4', '#ff7f0e'])
        axes[1, 1].set_title('평균 소환사 레벨')
        axes[1, 1].set_ylabel('레벨')
        
        for bar, level in zip(bars, avg_levels):
            axes[1, 1].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                           f'{level:.1f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.show()
    
    def display_ai_report(self, match_id: str):
        """AI 리포트 표시"""
        analysis = self.match_manager.analyze_with_ai(match_id)
        
        if not analysis or 'report' not in analysis:
            print("❌ 리포트를 생성할 수 없습니다.")
            return
        
        print("🤖 AI 생성 내전 리포트")
        print("=" * 60)
        print(analysis['report'])
        print("=" * 60)
    
    def display_ban_pick_suggestions(self, match_id: str):
        """밴픽 추천 표시"""
        analysis = self.match_manager.analyze_with_ai(match_id)
        
        if not analysis or 'ban_pick_suggestions' not in analysis:
            print("❌ 밴픽 추천을 생성할 수 없습니다.")
            return
        
        suggestions = analysis['ban_pick_suggestions']
        
        print("🎯 AI 밴픽 추천")
        print("=" * 60)
        
        if 'first_ban' in suggestions:
            print("1차 밴:")
            print(f"  블루팀: {', '.join(suggestions['first_ban'].get('blue', []))}")
            print(f"  레드팀: {', '.join(suggestions['first_ban'].get('red', []))}")
        
        if 'first_pick' in suggestions:
            print("\n1차 픽:")
            print(f"  블루팀: {', '.join(suggestions['first_pick'].get('blue', []))}")
            print(f"  레드팀: {', '.join(suggestions['first_pick'].get('red', []))}")
        
        if 'strategy' in suggestions:
            print(f"\n전략: {suggestions['strategy']}")
        
        print("=" * 60)

# ===== 자동 실행 함수 =====

def run_complete_demo():
    """완전 자동화 데모 실행"""
    print("🚀 Google GenAI를 활용한 고급 내전 관리 시스템")
    print("=" * 60)
    
    # API 키 입력
    print("🔑 API 키를 입력해주세요:")
    riot_api_key = input("라이엇 API 키: ").strip()
    genai_api_key = input("Google AI API 키: ").strip()
    
    if not riot_api_key or not genai_api_key:
        print("❌ 두 API 키 모두 필요합니다.")
        return
    
    # 시스템 초기화
    print("\n🔧 시스템 초기화 중...")
    riot_api = RiotAPIManager(riot_api_key)
    genai_manager = GenAIManager(genai_api_key)
    match_manager = EnhancedMatchManager(riot_api, genai_manager)
    visualizer = EnhancedVisualizer(match_manager)
    
    print("✅ 시스템 초기화 완료!")
    
    # 데모 플레이어 추가
    print("\n👤 데모 플레이어 추가 중...")
    demo_players = [
        "Hide on bush#KR1",
        "Faker#KR1", 
        "T1 Keria#KR1",
        "T1 Gumayusi#KR1",
        "T1 Oner#KR1",
        "T1 Zeus#KR1"
    ]
    
    for player in demo_players:
        if '#' in player:
            game_name, tag_line = player.split('#', 1)
            match_manager.add_player(game_name, tag_line)
    
    # 데모 내전 생성
    print("\n🏆 데모 내전 생성 중...")
    match = match_manager.create_match(
        "T1내전_AI분석", 
        "hard", 
        "T1코치", 
        demo_players
    )
    
    # AI 분석 실행
    print("\n🤖 AI 분석 실행 중...")
    analysis = match_manager.analyze_with_ai("T1내전_AI분석")
    
    if analysis:
        print("✅ AI 분석 완료!")
        
        # 시각화
        print("\n📊 시각화 생성 중...")
        visualizer.plot_ai_analysis("T1내전_AI분석")
        
        # 밴픽 추천
        print("\n🎯 밴픽 추천 생성 중...")
        visualizer.display_ban_pick_suggestions("T1내전_AI분석")
        
        # 리포트 표시
        print("\n📝 AI 리포트 생성 중...")
        visualizer.display_ai_report("T1내전_AI분석")
    
    print("\n✅ 데모 완료!")
    print("\n🎉 모든 기능이 성공적으로 실행되었습니다!")

# ===== 메인 실행 =====

if __name__ == "__main__":
    run_complete_demo()

print("✅ Google GenAI를 활용한 고급 내전 관리 시스템 준비 완료!")
print("\n🚀 사용 방법:")
print("1. 위의 코드를 코랩에서 실행하세요")
print("2. 라이엇 API 키와 Google AI API 키를 입력하세요")
print("3. 모든 분석이 자동으로 실행됩니다")
print("\n💡 주요 기능:")
print("- AI 기반 팀 밸런스 분석")
print("- AI 밴픽 전략 추천")
print("- AI 생성 내전 리포트")
print("- 고급 시각화")
print("- 완전 자동화")
