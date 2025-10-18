# ===== 코랩용 완전한 라이엇 API 내전 관리 시스템 =====
# 이 파일을 코랩에서 실행하세요!

# 1. 필요한 라이브러리 설치
!pip install requests pandas matplotlib seaborn plotly streamlit

# 2. 라이브러리 import
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
import streamlit as st
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

# 3. 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

print("✅ 라이브러리 설치 및 import 완료!")

# ===== 라이엇 API 클래스 =====

class RiotAPIManager:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_urls = {
            'asia': 'https://asia.api.riotgames.com',
            'kr': 'https://kr.api.riotgames.com'
        }
        self.rate_limits = {
            'personal': {'limit': 100, 'window': 120},
            'app': {'limit': 20000, 'window': 600}
        }
        
        # 챔피언 데이터
        self.champions = {
            1: {'name': '가렌', 'image': 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Garen.png'},
            2: {'name': '아리', 'image': 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Ahri.png'},
            3: {'name': '야스오', 'image': 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Yasuo.png'},
            4: {'name': '진', 'image': 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Jhin.png'},
            5: {'name': '럭스', 'image': 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Lux.png'},
            6: {'name': '다리우스', 'image': 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Darius.png'},
            7: {'name': '카타리나', 'image': 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Katarina.png'},
            8: {'name': '이즈리얼', 'image': 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Ezreal.png'},
            9: {'name': '소나', 'image': 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Sona.png'},
            10: {'name': '리신', 'image': 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/LeeSin.png'}
        }
    
    def get_summoner_by_riot_id(self, game_name: str, tag_line: str) -> Optional[Dict]:
        """라이엇 ID로 소환사 정보 조회"""
        url = f"{self.base_urls['asia']}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        headers = {'X-Riot-Token': self.api_key}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"❌ 플레이어를 찾을 수 없습니다: {game_name}#{tag_line}")
                return None
            else:
                print(f"❌ API 호출 실패: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 소환사 정보 조회 실패: {e}")
            return None
    
    def get_summoner_by_puuid(self, puuid: str) -> Optional[Dict]:
        """PUUID로 소환사 상세 정보 조회"""
        url = f"{self.base_urls['kr']}/lol/summoner/v4/summoners/by-puuid/{puuid}"
        headers = {'X-Riot-Token': self.api_key}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 소환사 상세 정보 조회 실패: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 소환사 상세 정보 조회 실패: {e}")
            return None
    
    def get_league_entries(self, summoner_id: str) -> List[Dict]:
        """소환사 리그 정보 조회 (솔로랭크만)"""
        url = f"{self.base_urls['kr']}/lol/league/v4/entries/by-summoner/{summoner_id}"
        headers = {'X-Riot-Token': self.api_key}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [entry for entry in data if entry.get('queueType') == 'RANKED_SOLO_5x5']
            else:
                return []
        except Exception as e:
            print(f"❌ 리그 정보 조회 실패: {e}")
            return []
    
    def get_champion_mastery(self, summoner_id: str, count: int = 10) -> List[Dict]:
        """챔피언 마스터리 정보 조회"""
        url = f"{self.base_urls['kr']}/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}"
        headers = {'X-Riot-Token': self.api_key}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data[:count]
            else:
                return []
        except Exception as e:
            print(f"❌ 챔피언 마스터리 조회 실패: {e}")
            return []
    
    def get_player_full_info(self, game_name: str, tag_line: str) -> Optional[Dict]:
        """플레이어의 전체 정보 조회"""
        try:
            account_info = self.get_summoner_by_riot_id(game_name, tag_line)
            if not account_info:
                return None
            
            puuid = account_info['puuid']
            summoner_info = self.get_summoner_by_puuid(puuid)
            if not summoner_info:
                return None
            
            summoner_id = summoner_info['id']
            league_entries = self.get_league_entries(summoner_id)
            champion_masteries = self.get_champion_mastery(summoner_id, 5)
            
            player_info = {
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
            
            return player_info
            
        except Exception as e:
            print(f"❌ 플레이어 정보 조회 실패: {e}")
            return None

# ===== 내전 관리 시스템 클래스 =====

class MatchManager:
    def __init__(self, riot_api: RiotAPIManager):
        self.riot_api = riot_api
        self.matches = []
        self.players = {}
    
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
        
        for player in players:
            if '#' in player:
                game_name, tag_line = player.split('#', 1)
                player_info = self.add_player(game_name, tag_line)
                if player_info:
                    match_data['players'].append(player_info)
        
        self.matches.append(match_data)
        print(f"✅ 내전 생성 완료: {match_id} ({len(match_data['players'])}명 참가)")
        return match_data
    
    def analyze_team_balance(self, match_id: str) -> Dict:
        """팀 밸런스 분석"""
        match = self.get_match(match_id)
        if not match:
            return {}
        
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
            lp_bonus = lp / 1000
            
            return base_score + rank_multiplier + lp_bonus
        
        player_scores = [calculate_player_score(player) for player in match['players']]
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
    
    def get_match(self, match_id: str) -> Optional[Dict]:
        """내전 조회"""
        for match in self.matches:
            if match['id'] == match_id:
                return match
        return None

# ===== 시각화 클래스 =====

class MatchVisualizer:
    def __init__(self, match_manager: MatchManager):
        self.match_manager = match_manager
    
    def plot_tier_distribution(self, figsize=(12, 8)):
        """티어 분포 시각화"""
        tier_dist = {}
        for player in self.match_manager.players.values():
            if player.get('league'):
                tier = player['league'].get('tier', 'UNRANKED')
                tier_dist[tier] = tier_dist.get(tier, 0) + 1
        
        if not tier_dist:
            print("❌ 티어 분포 데이터가 없습니다.")
            return
        
        tier_order = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER']
        ordered_tiers = {tier: tier_dist.get(tier, 0) for tier in tier_order if tier in tier_dist}
        
        plt.figure(figsize=figsize)
        bars = plt.bar(ordered_tiers.keys(), ordered_tiers.values(), 
                      color=['#8B4513', '#CD7F32', '#C0C0C0', '#FFD700', '#00CED1', '#9932CC', '#FF69B4', '#FF4500', '#FF0000'])
        
        plt.title('플레이어 티어 분포', fontsize=16, fontweight='bold')
        plt.xlabel('티어', fontsize=12)
        plt.ylabel('플레이어 수', fontsize=12)
        plt.xticks(rotation=45)
        
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
        
        teams = ['블루팀', '레드팀']
        scores = [balance['blue_score'], balance['red_score']]
        colors = ['#1f77b4', '#ff7f0e']
        
        bars = ax1.bar(teams, scores, color=colors)
        ax1.set_title('팀 밸런스 점수', fontsize=14, fontweight='bold')
        ax1.set_ylabel('점수', fontsize=12)
        
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.2f}', ha='center', va='bottom')
        
        balance_ratio = balance['balance_ratio']
        ax2.pie([balance_ratio, 1-balance_ratio], 
                labels=['밸런스', '불균형'], 
                colors=['#2ecc71', '#e74c3c'],
                autopct='%1.1f%%')
        ax2.set_title(f'밸런스 비율: {balance_ratio:.2f}', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.show()

# ===== 사용 예시 =====

def demo_usage():
    """데모 사용 예시"""
    print("🎮 라이엇 API 내전 관리 시스템 데모")
    print("="*50)
    
    # API 키 입력 (실제 사용 시에는 환경변수 사용)
    api_key = input("라이엇 API 키를 입력하세요: ").strip()
    
    if not api_key:
        print("❌ API 키가 필요합니다.")
        return
    
    # 시스템 초기화
    riot_api = RiotAPIManager(api_key)
    match_manager = MatchManager(riot_api)
    visualizer = MatchVisualizer(match_manager)
    
    print("\n✅ 시스템 초기화 완료!")
    
    # 데모 플레이어 추가
    print("\n👤 데모 플레이어 추가 중...")
    demo_players = [
        "Hide on bush#KR1",  # 실제 플레이어 ID로 변경
        "Faker#KR1",
        "T1 Keria#KR1"
    ]
    
    for player in demo_players:
        if '#' in player:
            game_name, tag_line = player.split('#', 1)
            match_manager.add_player(game_name, tag_line)
    
    # 데모 내전 생성
    print("\n🏆 데모 내전 생성 중...")
    match = match_manager.create_match(
        "데모내전001", 
        "soft", 
        "관리자", 
        demo_players
    )
    
    # 팀 밸런스 분석
    print("\n⚖️ 팀 밸런스 분석 중...")
    balance = match_manager.analyze_team_balance("데모내전001")
    if balance:
        print(f"블루팀 점수: {balance['blue_score']:.2f}")
        print(f"레드팀 점수: {balance['red_score']:.2f}")
        print(f"밸런스 비율: {balance['balance_ratio']:.2f}")
        
        # 시각화
        visualizer.plot_team_balance("데모내전001")
    
    # 티어 분포 시각화
    print("\n📊 티어 분포 시각화 중...")
    visualizer.plot_tier_distribution()
    
    print("\n✅ 데모 완료!")

# 실행
if __name__ == "__main__":
    demo_usage()

print("✅ 코랩용 라이엇 API 내전 관리 시스템 준비 완료!")
print("\n🚀 사용 방법:")
print("1. 위의 코드를 코랩에서 실행하세요")
print("2. 라이엇 API 키를 입력하세요")
print("3. 데모가 자동으로 실행됩니다")
print("\n💡 실제 사용 시에는 demo_usage() 함수를 수정하여 원하는 기능을 사용하세요!")
