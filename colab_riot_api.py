# ===== 라이엇 API 클래스 =====

class RiotAPIManager:
    def __init__(self, api_key: str):
        """
        라이엇 API 매니저 초기화
        
        Args:
            api_key (str): 라이엇 API 키
        """
        self.api_key = api_key
        self.base_urls = {
            'asia': 'https://asia.api.riotgames.com',
            'kr': 'https://kr.api.riotgames.com'
        }
        self.rate_limits = {
            'personal': {'limit': 100, 'window': 120},
            'app': {'limit': 20000, 'window': 600}
        }
        
        # 챔피언 데이터 (실제로는 API에서 가져와야 함)
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
                # 솔로랭크만 필터링
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
            # 1. 라이엇 ID로 PUUID 조회
            account_info = self.get_summoner_by_riot_id(game_name, tag_line)
            if not account_info:
                return None
            
            puuid = account_info['puuid']
            
            # 2. PUUID로 소환사 상세 정보 조회
            summoner_info = self.get_summoner_by_puuid(puuid)
            if not summoner_info:
                return None
            
            summoner_id = summoner_info['id']
            
            # 3. 리그 정보 조회
            league_entries = self.get_league_entries(summoner_id)
            
            # 4. 챔피언 마스터리 조회
            champion_masteries = self.get_champion_mastery(summoner_id, 5)
            
            # 5. 정보 통합
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

print("✅ RiotAPIManager 클래스 정의 완료!")
