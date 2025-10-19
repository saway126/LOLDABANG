<template>
  <div class="banpick-container">
    <!-- 헤더 -->
    <div class="banpick-header">
      <h1>🎮 실시간 밴픽 관리</h1>
      <div class="header-controls">
        <button @click="refreshData" :disabled="loading" class="refresh-btn">
          <span v-if="loading">🔄</span>
          <span v-else>새로고침</span>
        </button>
        <div class="connection-status" :class="wsConnected ? 'connected' : 'polling'">
          {{ wsConnected ? '🟢 실시간 연결됨' : '🔄 폴링 모드 (30초마다 업데이트)' }}
        </div>
        <!-- 알림 컴포넌트 -->
        <RealtimeNotification ref="notificationComponent" />
      </div>
    </div>

    <!-- 밴픽 인터페이스 -->
    <div class="banpick-interface">
      <div class="match-header">
        <h3>🎮 밴픽 관리</h3>
        <div class="match-controls">
          <button @click="startBanPick" :disabled="banPickPhase !== 'waiting'" class="start-btn">
            밴픽 시작
          </button>
          <button @click="resetBanPick" class="reset-btn">
            리셋
          </button>
          <button @click="saveBanPick" :disabled="banPickPhase === 'waiting'" class="save-btn">
            💾 저장
          </button>
        </div>
      </div>

      <!-- 밴픽 단계 표시 -->
      <div class="phase-indicator">
        <div class="phase" :class="{ active: banPickPhase === 'ban' }">
          밴 단계
        </div>
        <div class="phase" :class="{ active: banPickPhase === 'pick' }">
          픽 단계
        </div>
        <div class="phase" :class="{ active: banPickPhase === 'completed' }">
          완료
        </div>
      </div>

      <!-- 팀 정보 -->
      <div class="teams-section">
        <div class="team team-blue">
          <h4>🔵 블루팀</h4>
          <div class="team-players">
            <div v-for="player in blueTeam" :key="player.id" class="player-card">
              <div class="player-name">{{ player.name }}</div>
              <div class="player-tier">{{ player.tier }}</div>
            </div>
          </div>
          <div class="team-bans">
            <h5>밴된 챔피언</h5>
            <div class="banned-champions">
              <div 
                v-for="champion in blueTeamBans" 
                :key="champion.id"
                class="champion-ban"
                @click="removeBan(champion, 'blue')"
              >
                <img :src="champion.image" :alt="champion.name" />
                <span>{{ champion.name }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="team team-red">
          <h4>🔴 레드팀</h4>
          <div class="team-players">
            <div v-for="player in redTeam" :key="player.id" class="player-card">
              <div class="player-name">{{ player.name }}</div>
              <div class="player-tier">{{ player.tier }}</div>
            </div>
          </div>
          <div class="team-bans">
            <h5>밴된 챔피언</h5>
            <div class="banned-champions">
              <div 
                v-for="champion in redTeamBans" 
                :key="champion.id"
                class="champion-ban"
                @click="removeBan(champion, 'red')"
              >
                <img :src="champion.image" :alt="champion.name" />
                <span>{{ champion.name }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 챔피언 검색 및 선택 -->
      <div class="champion-selection">
        <div class="search-section">
          <input 
            v-model="championSearch" 
            @input="searchChampions"
            placeholder="챔피언 검색..."
            class="champion-search"
          />
        </div>
        
        <div class="champions-grid">
          <div 
            v-for="champion in filteredChampions" 
            :key="champion.id"
            class="champion-card"
            :class="{ 
              banned: isChampionBanned(champion.id),
              picked: isChampionPicked(champion.id)
            }"
            @click="selectChampion(champion)"
          >
            <img :src="champion.image" :alt="champion.name" />
            <span class="champion-name">{{ champion.name }}</span>
            <div v-if="isChampionBanned(champion.id)" class="ban-indicator">🚫</div>
            <div v-if="isChampionPicked(champion.id)" class="pick-indicator">✅</div>
          </div>
        </div>
      </div>

      <!-- 이전 게임 기록 -->
      <div class="game-history">
        <h4>📊 이전 게임 기록</h4>
        <div v-if="gameHistory.length === 0" class="no-history">
          이전 게임 기록이 없습니다
        </div>
        <div v-else class="history-list">
          <div 
            v-for="game in gameHistory" 
            :key="game.id"
            class="history-item"
          >
            <div class="game-info">
              <div class="game-date">{{ game.date }}</div>
              <div class="game-winner">{{ game.winner }} 승리</div>
            </div>
            <div class="game-champions">
              <div class="team-champions">
                <span class="team-label">블루팀:</span>
                <div class="champion-list">
                  <span 
                    v-for="champion in game.blueTeam" 
                    :key="champion"
                    class="champion-tag"
                  >
                    {{ champion }}
                  </span>
                </div>
              </div>
              <div class="team-champions">
                <span class="team-label">레드팀:</span>
                <div class="champion-list">
                  <span 
                    v-for="champion in game.redTeam" 
                    :key="champion"
                    class="champion-tag"
                  >
                    {{ champion }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import RealtimeNotification from '../components/RealtimeNotification.vue'

// API 설정
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://loldabang-production.up.railway.app/api'
const WS_URL = import.meta.env.VITE_WS_URL || 'wss://loldabang-production.up.railway.app/ws'

// 반응형 데이터
const loading = ref(false)
const wsConnected = ref(false)
const notificationComponent = ref(null)

// 밴픽 관련
const banPickPhase = ref('waiting') // waiting, ban, pick, completed
const blueTeam = ref([])
const redTeam = ref([])
const blueTeamBans = ref([])
const redTeamBans = ref([])
const blueTeamPicks = ref([])
const redTeamPicks = ref([])

// 챔피언 관련
const champions = ref([])
const championSearch = ref('')
const filteredChampions = ref([])

// 게임 기록
const gameHistory = ref([])

// 계산된 속성
const isChampionBanned = (championId) => {
  return [...blueTeamBans.value, ...redTeamBans.value].some(ban => ban.id === championId)
}

const isChampionPicked = (championId) => {
  return [...blueTeamPicks.value, ...redTeamPicks.value].some(pick => pick.id === championId)
}

// 메서드
const fetchChampions = async () => {
  try {
    const response = await fetch('https://ddragon.leagueoflegends.com/cdn/13.24.1/data/ko_KR/champion.json')
    if (response.ok) {
      const data = await response.json()
      champions.value = Object.values(data.data).map(champion => ({
        id: parseInt(champion.key),
        name: champion.name,
        image: `https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/${champion.id}.png`
      }))
      filteredChampions.value = champions.value
    }
  } catch (error) {
    console.error('챔피언 데이터 로드 실패:', error)
  }
}

const fetchGameHistory = async () => {
  try {
    // 실제로는 백엔드에서 게임 기록을 가져와야 함
    // 임시 데이터
    gameHistory.value = [
      {
        id: 1,
        date: new Date().toLocaleDateString('ko-KR'),
        winner: '블루팀',
        blueTeam: ['아리', '리 신', '아지르', '진', '쓰레쉬'],
        redTeam: ['야스오', '그레이브즈', '빅토르', '케이틀린', '레오나']
      }
    ]
  } catch (error) {
    console.error('게임 기록 조회 실패:', error)
  }
}

const searchChampions = () => {
  if (!championSearch.value) {
    filteredChampions.value = champions.value
  } else {
    filteredChampions.value = champions.value.filter(champion =>
      champion.name.toLowerCase().includes(championSearch.value.toLowerCase())
    )
  }
}

const selectChampion = (champion) => {
  if (isChampionBanned(champion.id) || isChampionPicked(champion.id)) {
    return
  }

  if (banPickPhase.value === 'ban') {
    // 밴 단계
    if (blueTeamBans.value.length < 3) {
      blueTeamBans.value.push(champion)
    } else if (redTeamBans.value.length < 3) {
      redTeamBans.value.push(champion)
    }
    
    // 밴이 완료되면 픽 단계로
    if (blueTeamBans.value.length === 3 && redTeamBans.value.length === 3) {
      banPickPhase.value = 'pick'
    }
  } else if (banPickPhase.value === 'pick') {
    // 픽 단계
    if (blueTeamPicks.value.length < 5) {
      blueTeamPicks.value.push(champion)
    } else if (redTeamPicks.value.length < 5) {
      redTeamPicks.value.push(champion)
    }
    
    // 픽이 완료되면 완료 단계로
    if (blueTeamPicks.value.length === 5 && redTeamPicks.value.length === 5) {
      banPickPhase.value = 'completed'
    }
  }
}

const removeBan = (champion, team) => {
  if (team === 'blue') {
    blueTeamBans.value = blueTeamBans.value.filter(ban => ban.id !== champion.id)
  } else {
    redTeamBans.value = redTeamBans.value.filter(ban => ban.id !== champion.id)
  }
}

const startBanPick = () => {
  banPickPhase.value = 'ban'
  blueTeamBans.value = []
  redTeamBans.value = []
  blueTeamPicks.value = []
  redTeamPicks.value = []
}

const resetBanPick = () => {
  banPickPhase.value = 'waiting'
  blueTeamBans.value = []
  redTeamBans.value = []
  blueTeamPicks.value = []
  redTeamPicks.value = []
}

const saveBanPick = async () => {
  try {
    const banPickData = {
      blueTeamBans: blueTeamBans.value,
      redTeamBans: redTeamBans.value,
      blueTeamPicks: blueTeamPicks.value,
      redTeamPicks: redTeamPicks.value,
      phase: banPickPhase.value,
      timestamp: new Date().toISOString()
    }
    
    // 로컬 스토리지에 저장
    localStorage.setItem('banPickData', JSON.stringify(banPickData))
    
    // 백엔드에 저장 (선택사항)
    const response = await fetch(`${API_BASE_URL}/banpick/save`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(banPickData)
    })
    
    if (response.ok) {
      showNotification('밴픽 결과가 저장되었습니다!', 'success')
    } else {
      showNotification('로컬에만 저장되었습니다.', 'warning')
    }
  } catch (error) {
    console.error('밴픽 저장 실패:', error)
    showNotification('밴픽 저장에 실패했습니다.', 'error')
  }
}

const refreshData = () => {
  // 데이터 새로고침 (필요시 구현)
  console.log('데이터 새로고침')
}

// 사용하지 않는 함수들 제거됨

// 사용하지 않는 함수들 제거됨

const showNotification = (message, type = 'info') => {
  // 알림 컴포넌트에 전달
  if (notificationComponent.value) {
    notificationComponent.value.addNotification({
      type,
      title: getNotificationTitle(type),
      message,
      timestamp: new Date()
    })
  }
  
  // 브라우저 알림 API 사용
  if ('Notification' in window) {
    if (Notification.permission === 'granted') {
      new Notification('롤다방 알림', {
        body: message,
        icon: '/favicon.ico'
      })
    } else if (Notification.permission !== 'denied') {
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          new Notification('롤다방 알림', {
            body: message,
            icon: '/favicon.ico'
          })
        }
      })
    }
  }
  
  // 콘솔에도 로그 출력
  const timestamp = new Date().toLocaleTimeString('ko-KR')
  console.log(`[${timestamp}] ${type.toUpperCase()}: ${message}`)
}

const getNotificationTitle = (type) => {
  const titles = {
    'success': '성공',
    'error': '오류',
    'warning': '경고',
    'info': '알림'
  }
  return titles[type] || '알림'
}

// 라이프사이클
onMounted(() => {
  fetchChampions()
  fetchGameHistory()
  
  // 임시 팀 데이터 로드
  blueTeam.value = [
    { id: 1, name: 'Player1', tier: 'Gold I' },
    { id: 2, name: 'Player2', tier: 'Platinum IV' },
    { id: 3, name: 'Player3', tier: 'Gold II' },
    { id: 4, name: 'Player4', tier: 'Silver I' },
    { id: 5, name: 'Player5', tier: 'Gold III' }
  ]
  redTeam.value = [
    { id: 6, name: 'Player6', tier: 'Platinum III' },
    { id: 7, name: 'Player7', tier: 'Gold I' },
    { id: 8, name: 'Player8', tier: 'Silver II' },
    { id: 9, name: 'Player9', tier: 'Gold IV' },
    { id: 10, name: 'Player10', tier: 'Platinum II' }
  ]
})

onUnmounted(() => {
  // 정리 작업
})

// 챔피언 검색 감시
watch(championSearch, searchChampions)
</script>

<style scoped>
.banpick-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  background: linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
  min-height: 100vh;
}

.banpick-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  background: rgba(139, 69, 19, 0.1);
  padding: 20px;
  border-radius: 15px;
  backdrop-filter: blur(10px);
}

.banpick-header h1 {
  color: white;
  margin: 0;
  font-size: 2rem;
  font-weight: bold;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 20px;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 10px 20px;
  border-radius: 25px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.connection-status {
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: bold;
  font-size: 0.9rem;
}

.connection-status.connected {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
}

.connection-status.disconnected {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
}

.connection-status.polling {
  background: rgba(139, 69, 19, 0.1);
  color: var(--text-secondary);
  border: 1px solid rgba(139, 69, 19, 0.2);
}

.active-matches, .banpick-interface {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 25px;
  margin-bottom: 25px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.active-matches h2, .banpick-interface h3 {
  color: #333;
  margin-bottom: 20px;
  font-size: 1.5rem;
  font-weight: bold;
}

.no-matches {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
  background: rgba(139, 69, 19, 0.03);
  border-radius: 12px;
}

.no-matches-icon {
  font-size: 2rem;
  margin-bottom: 12px;
  opacity: 0.6;
}

.matches-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
}

.match-item {
  background: white;
  border-radius: 10px;
  padding: 15px;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.match-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.match-item.active {
  border-color: #667eea;
  background: #f0f4ff;
}

.match-content {
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.match-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  flex-wrap: wrap;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 15px;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: bold;
  transition: all 0.3s ease;
  min-width: 70px;
}

.action-btn.start {
  background: rgba(139, 69, 19, 0.1);
  color: var(--primary-color);
  border: 1px solid var(--primary-color);
}

.action-btn.start:hover {
  background: var(--primary-color);
  color: white;
}

.action-btn.end {
  background: rgba(255, 152, 0, 0.1);
  color: var(--warning-color);
  border: 1px solid var(--warning-color);
}

.action-btn.end:hover {
  background: var(--warning-color);
  color: white;
}

.action-btn.close {
  background: rgba(244, 67, 54, 0.1);
  color: var(--error-color);
  border: 1px solid var(--error-color);
}

.action-btn.close:hover {
  background: var(--error-color);
  color: white;
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.match-info {
  margin-bottom: 10px;
}

.match-id {
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.match-host {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.match-type {
  color: #667eea;
  font-size: 0.8rem;
  font-weight: bold;
}

.match-status {
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: bold;
  text-align: center;
}

.match-status.open {
  background: #e8f5e8;
  color: #4CAF50;
}

.match-status.in_progress {
  background: #fff3e0;
  color: #FF9800;
}

.phase-indicator {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 30px;
}

.phase {
  padding: 10px 20px;
  border-radius: 25px;
  background: #f0f0f0;
  color: #666;
  font-weight: bold;
  transition: all 0.3s ease;
}

.phase.active {
  background: #667eea;
  color: white;
}

.teams-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 30px;
}

.team {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
}

.team h4 {
  margin-bottom: 15px;
  color: #333;
}

.team-players {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
  margin-bottom: 20px;
}

.player-card {
  background: white;
  border-radius: 8px;
  padding: 10px;
  text-align: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.player-name {
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.player-tier {
  font-size: 0.8rem;
  color: #666;
}

.team-bans h5 {
  margin-bottom: 10px;
  color: #333;
}

.banned-champions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.champion-ban {
  display: flex;
  align-items: center;
  background: #ffebee;
  border-radius: 8px;
  padding: 5px 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.champion-ban:hover {
  background: #ffcdd2;
}

.champion-ban img {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  margin-right: 5px;
}

.champion-selection {
  margin-bottom: 30px;
}

.search-section {
  margin-bottom: 20px;
}

.champion-search {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 25px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s ease;
}

.champion-search:focus {
  border-color: #667eea;
}

.champions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 10px;
  max-height: 400px;
  overflow-y: auto;
}

.champion-card {
  position: relative;
  background: white;
  border-radius: 8px;
  padding: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.champion-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.champion-card.banned {
  opacity: 0.5;
  cursor: not-allowed;
}

.champion-card.picked {
  border-color: #4CAF50;
  background: #e8f5e8;
}

.champion-card img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-bottom: 5px;
}

.champion-name {
  font-size: 0.7rem;
  color: #333;
  display: block;
}

.ban-indicator, .pick-indicator {
  position: absolute;
  top: 2px;
  right: 2px;
  font-size: 0.8rem;
}

.game-history {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
}

.game-history h4 {
  margin-bottom: 15px;
  color: #333;
}

.no-history {
  text-align: center;
  color: #666;
  padding: 20px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.history-item {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.game-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.game-date {
  color: #666;
  font-size: 0.9rem;
}

.game-winner {
  font-weight: bold;
  color: #4CAF50;
}

.team-champions {
  margin-bottom: 8px;
}

.team-label {
  font-weight: bold;
  color: #333;
  margin-right: 10px;
}

.champion-list {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 5px;
}

.champion-tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
}

@media (max-width: 768px) {
  .teams-section {
    grid-template-columns: 1fr;
  }
  
  .champions-grid {
    grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
  }
  
  .champion-card img {
    width: 30px;
    height: 30px;
  }
  
  .champion-name {
    font-size: 0.6rem;
  }
}

/* 저장 버튼 스타일 */
.save-btn {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3);
}

.save-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #45a049 0%, #3d8b40 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.4);
}

.save-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
</style>
