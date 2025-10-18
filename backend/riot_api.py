import requests
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
import os
from datetime import datetime, timedelta

class RiotAPIService:
    def __init__(self):
        self.api_key = os.getenv('RIOT_API_KEY', '')
        self.base_urls = {
            'asia': 'https://asia.api.riotgames.com',
            'kr': 'https://kr.api.riotgames.com'
        }
        self.rate_limits = {
            'personal': {'limit': 100, 'window': 120},  # 2분당 100개
            'app': {'limit': 20000, 'window': 600}      # 10분당 20,000개
        }
        
    async def get_summoner_by_riot_id(self, game_name: str, tag_line: str) -> Optional[Dict]:
        """라이엇 ID로 소환사 정보 조회"""
        if not self.api_key:
            raise ValueError("RIOT_API_KEY가 설정되지 않았습니다.")
            
        url = f"{self.base_urls['asia']}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        headers = {'X-Riot-Token': self.api_key}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        return None
                    else:
                        raise Exception(f"API 호출 실패: {response.status}")
            except Exception as e:
                print(f"소환사 정보 조회 실패: {e}")
                return None
    
    async def get_summoner_by_puuid(self, puuid: str) -> Optional[Dict]:
        """PUUID로 소환사 상세 정보 조회"""
        url = f"{self.base_urls['kr']}/lol/summoner/v4/summoners/by-puuid/{puuid}"
        headers = {'X-Riot-Token': self.api_key}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"소환사 상세 정보 조회 실패: {response.status}")
            except Exception as e:
                print(f"소환사 상세 정보 조회 실패: {e}")
                return None
    
    async def get_league_entries(self, summoner_id: str) -> List[Dict]:
        """소환사 리그 정보 조회 (솔로랭크만)"""
        url = f"{self.base_urls['kr']}/lol/league/v4/entries/by-summoner/{summoner_id}"
        headers = {'X-Riot-Token': self.api_key}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        # 솔로랭크만 필터링
                        return [entry for entry in data if entry.get('queueType') == 'RANKED_SOLO_5x5']
                    else:
                        return []
            except Exception as e:
                print(f"리그 정보 조회 실패: {e}")
                return []
    
    async def get_champion_mastery(self, summoner_id: str, count: int = 10) -> List[Dict]:
        """챔피언 마스터리 정보 조회"""
        url = f"{self.base_urls['kr']}/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}"
        headers = {'X-Riot-Token': self.api_key}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data[:count]  # 상위 N개만 반환
                    else:
                        return []
            except Exception as e:
                print(f"챔피언 마스터리 조회 실패: {e}")
                return []
    
    async def get_champion_data(self, champion_id: int) -> Optional[Dict]:
        """챔피언 데이터 조회 (정적 데이터)"""
        # 실제로는 챔피언 데이터를 미리 저장해두고 사용
        # 여기서는 간단한 예시만 제공
        champion_data = {
            "id": champion_id,
            "name": f"Champion_{champion_id}",
            "image_url": f"https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/{champion_id}.png"
        }
        return champion_data
    
    async def get_player_full_info(self, game_name: str, tag_line: str) -> Optional[Dict]:
        """플레이어의 전체 정보 조회 (소환사 + 리그 + 챔피언 마스터리)"""
        try:
            # 1. 라이엇 ID로 PUUID 조회
            account_info = await self.get_summoner_by_riot_id(game_name, tag_line)
            if not account_info:
                return None
            
            puuid = account_info['puuid']
            
            # 2. PUUID로 소환사 상세 정보 조회
            summoner_info = await self.get_summoner_by_puuid(puuid)
            if not summoner_info:
                return None
            
            summoner_id = summoner_info['id']
            
            # 3. 리그 정보 조회
            league_entries = await self.get_league_entries(summoner_id)
            
            # 4. 챔피언 마스터리 조회
            champion_masteries = await self.get_champion_mastery(summoner_id, 5)
            
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
            print(f"플레이어 정보 조회 실패: {e}")
            return None

# 전역 인스턴스
riot_api = RiotAPIService()
