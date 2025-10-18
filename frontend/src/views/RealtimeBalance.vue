<template>
  <div class="balance-container">
    <!-- 헤더 -->
    <div class="balance-header">
      <h1>⚖️ 실시간 팀 밸런스 분석</h1>
      <div class="header-controls">
        <button @click="refreshData" :disabled="loading" class="refresh-btn">
          <span v-if="loading">🔄</span>
          <span v-else>새로고침</span>
        </button>
        <div class="connection-status" :class="wsConnected ? 'connected' : 'disconnected'">
          {{ wsConnected ? '🟢 연결됨' : '🔴 연결 끊김' }}
        </div>
      </div>
    </div>

    <!-- 활성 내전 선택 -->
    <div class="match-selection">
      <h2>🎮 내전 선택</h2>
      <div v-if="activeMatches.length === 0" class="no-matches">
        <div class="no-matches-icon">😴</div>
        <p>현재 활성 내전이 없습니다</p>
      </div>
      <div v-else class="matches-grid">
        <div 
          v-for="match in activeMatches" 
          :key="match.id"
          class="match-card"
          :class="{ active: selectedMatch?.id === match.id }"
          @click="selectMatch(match)"
        >
          <div class="match-info">
            <div class="match-id">{{ match.customId }}</div>
            <div class="match-host">{{ match.host }}</div>
            <div class="match-type">{{ getTypeText(match.type) }}</div>
          </div>
          <div class="match-status" :class="match.status">
            {{ getStatusText(match.status) }}
          </div>
        </div>
      </div>
    </div>

    <!-- 팀 밸런스 분석 -->
    <div v-if="selectedMatch" class="balance-analysis">
      <div class="analysis-header">
        <h3>{{ selectedMatch.customId }} - 팀 밸런스 분석</h3>
        <div class="analysis-controls">
          <button @click="startAnalysis" :disabled="isAnalyzing" class="analyze-btn">
            {{ isAnalyzing ? '분석 중...' : '밸런스 분석 시작' }}
          </button>
          <button @click="resetAnalysis" class="reset-btn">
            리셋
          </button>
        </div>
      </div>

      <!-- 티어별 환산 점수 기준표 -->
      <div class="tier-score-guide">
        <h4>📊 티어별 환산 점수 기준표</h4>
        <div class="score-guide-content">
          <div class="tier-scores">
            <div class="tier-score-item">
              <span class="tier-name">챌린저</span>
              <span class="tier-score">900점</span>
            </div>
            <div class="tier-score-item">
              <span class="tier-name">그마</span>
              <span class="tier-score">800점</span>
            </div>
            <div class="tier-score-item">
              <span class="tier-name">마스터</span>
              <span class="tier-score">700점</span>
            </div>
            <div class="tier-score-item">
              <span class="tier-name">다이아</span>
              <span class="tier-score">600점</span>
            </div>
            <div class="tier-score-item">
              <span class="tier-name">플래티넘</span>
              <span class="tier-score">500점</span>
            </div>
            <div class="tier-score-item">
              <span class="tier-name">골드</span>
              <span class="tier-score">400점</span>
            </div>
            <div class="tier-score-item">
              <span class="tier-name">실버</span>
              <span class="tier-score">300점</span>
            </div>
            <div class="tier-score-item">
              <span class="tier-name">브론즈</span>
              <span class="tier-score">200점</span>
            </div>
            <div class="tier-score-item">
              <span class="tier-name">아이언</span>
              <span class="tier-score">100점</span>
            </div>
          </div>
          <div class="score-details">
            <p><strong>추가 점수:</strong></p>
            <ul>
              <li>랭크 보너스: I(75점), II(50점), III(25점), IV(0점)</li>
              <li>LP 보너스: 10LP당 1점</li>
              <li>챔피언 마스터리: 상위 3개 챔피언 평균 점수 × 0.1</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 플레이어 추가 섹션 -->
      <div class="player-input-section">
        <h4>👥 플레이어 추가</h4>
        <div class="player-input">
          <input 
            v-model="newPlayer.gameName" 
            placeholder="게임명"
            class="player-input-field"
          />
          <input 
            v-model="newPlayer.tagLine" 
            placeholder="태그"
            class="player-input-field"
          />
          <select v-model="newPlayer.preferredRole" class="role-select">
            <option value="">라인 선택</option>
            <option value="TOP">탑</option>
            <option value="JUNGLE">정글</option>
            <option value="MID">미드</option>
            <option value="ADC">원딜</option>
            <option value="SUPPORT">서포터</option>
          </select>
          <button @click="addPlayer" :disabled="!newPlayer.gameName || !newPlayer.tagLine" class="add-player-btn">
            추가
          </button>
        </div>
      </div>

      <!-- 플레이어 목록 -->
      <div class="players-section">
        <h4>📋 참가 플레이어 ({{ players.length }}명)</h4>
        <div v-if="players.length === 0" class="no-players">
          플레이어를 추가해주세요
        </div>
        <div v-else class="players-grid">
          <div 
            v-for="(player, index) in players" 
            :key="index"
            class="player-card"
            :class="{ loading: player.loading }"
          >
            <div class="player-info">
              <div class="player-name">{{ player.gameName }}#{{ player.tagLine }}</div>
              <div class="player-details">
                <div class="player-tier">{{ player.tier || '로딩 중...' }} {{ player.rank || '' }}</div>
                <div class="player-lp" v-if="player.lp > 0">{{ player.lp }}LP</div>
                <div class="player-role" v-if="player.preferredRole !== 'FILL'">
                  {{ getRoleText(player.preferredRole) }}
                </div>
              </div>
              <div class="player-score">점수: {{ player.score || 0 }}</div>
            </div>
            <div class="player-actions">
              <button @click="removePlayer(index)" class="remove-btn">✕</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 팀 구성 결과 -->
      <div v-if="teamComposition" class="team-composition">
        <h4>🏆 팀 구성 결과</h4>
        <div class="balance-summary">
          <div class="balance-score">
            <span class="label">밸런스 점수:</span>
            <span class="value" :class="getBalanceClass(teamComposition.balanceScore)">
              {{ teamComposition.balanceScore }}
            </span>
          </div>
          <div class="balance-status">
            <span class="label">상태:</span>
            <span class="value" :class="teamComposition.isBalanced ? 'balanced' : 'unbalanced'">
              {{ teamComposition.isBalanced ? '균형' : '불균형' }}
            </span>
          </div>
        </div>

        <div class="teams-display">
          <div class="team team-blue">
            <h5>🔵 블루팀 ({{ teamComposition.team1.length }}명)</h5>
            <div class="team-score">점수: {{ teamComposition.team1Score }}</div>
            <div class="team-players">
              <div 
                v-for="player in teamComposition.team1" 
                :key="player.name"
                class="team-player"
                :class="{ 'team-leader': player.isTeamLeader }"
              >
                <div class="player-info">
                  <div class="player-name">
                    {{ player.name }}
                    <span v-if="player.isTeamLeader" class="leader-badge">👑</span>
                  </div>
                  <div class="player-role">{{ getRoleText(player.role) }}</div>
                </div>
                <div class="player-stats">
                  <div class="player-tier">{{ player.tier }} {{ player.rank }}</div>
                  <div class="player-score">{{ player.score }}점</div>
                </div>
              </div>
            </div>
          </div>

          <div class="team team-red">
            <h5>🔴 레드팀 ({{ teamComposition.team2.length }}명)</h5>
            <div class="team-score">점수: {{ teamComposition.team2Score }}</div>
            <div class="team-players">
              <div 
                v-for="player in teamComposition.team2" 
                :key="player.name"
                class="team-player"
                :class="{ 'team-leader': player.isTeamLeader }"
              >
                <div class="player-info">
                  <div class="player-name">
                    {{ player.name }}
                    <span v-if="player.isTeamLeader" class="leader-badge">👑</span>
                  </div>
                  <div class="player-role">{{ getRoleText(player.role) }}</div>
                </div>
                <div class="player-stats">
                  <div class="player-tier">{{ player.tier }} {{ player.rank }}</div>
                  <div class="player-score">{{ player.score }}점</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 라인 분포 -->
        <div v-if="teamComposition.roleDistribution" class="role-distribution">
          <h5>📊 라인별 분포</h5>
          <div class="role-stats">
            <div 
              v-for="role in teamComposition.roleDistribution" 
              :key="role.role"
              class="role-stat"
            >
              <div class="role-name">{{ getRoleText(role.role) }}</div>
              <div class="role-count">{{ role.count }}명</div>
              <div class="role-players">{{ role.players.join(', ') }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- AI 분석 결과 -->
      <div v-if="aiAnalysis" class="ai-analysis">
        <h4>🤖 AI 분석 결과</h4>
        <div class="analysis-content">
          <div class="analysis-text">{{ aiAnalysis }}</div>
        </div>
      </div>

      <!-- 시각화 -->
      <div v-if="teamComposition" class="visualization">
        <h4>📊 시각화</h4>
        <div class="charts-container">
          <div class="chart">
            <h5>팀 점수 비교</h5>
            <div class="score-chart">
              <div class="chart-bar">
                <div class="bar-label">블루팀</div>
                <div class="bar-container">
                  <div 
                    class="bar-fill blue" 
                    :style="{ width: getBarWidth(teamComposition.team1Score, teamComposition.team2Score) }"
                  ></div>
                </div>
                <div class="bar-value">{{ teamComposition.team1Score }}</div>
              </div>
              <div class="chart-bar">
                <div class="bar-label">레드팀</div>
                <div class="bar-container">
                  <div 
                    class="bar-fill red" 
                    :style="{ width: getBarWidth(teamComposition.team2Score, teamComposition.team1Score) }"
                  ></div>
                </div>
                <div class="bar-value">{{ teamComposition.team2Score }}</div>
              </div>
            </div>
          </div>

          <div class="chart">
            <h5>티어 분포</h5>
            <div class="tier-distribution">
              <div 
                v-for="tier in tierDistribution" 
                :key="tier.name"
                class="tier-item"
              >
                <div class="tier-name">{{ tier.name }}</div>
                <div class="tier-count">{{ tier.count }}명</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useWebSocket } from '../composables/useWebSocket'

// API 설정
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://loldabang-production.up.railway.app/api'
const WS_URL = import.meta.env.VITE_WS_URL || 'wss://loldabang-production.up.railway.app/ws'

// 반응형 데이터
const activeMatches = ref([])
const selectedMatch = ref(null)
const players = ref([])
const teamComposition = ref(null)
const aiAnalysis = ref('')
const loading = ref(false)
const isAnalyzing = ref(false)
const wsConnected = ref(false)

// 새 플레이어 입력
const newPlayer = ref({
  gameName: '',
  tagLine: '',
  preferredRole: ''
})

// WebSocket 연결
const { isConnected, send } = useWebSocket(WS_URL, {
  onMessage: handleWebSocketMessage,
  onOpen: () => {
    wsConnected.value = true
    console.log('밸런스 WebSocket 연결됨')
  },
  onClose: () => {
    wsConnected.value = false
    console.log('밸런스 WebSocket 연결 끊김')
  }
})

// 계산된 속성
const tierDistribution = computed(() => {
  const tiers = {}
  players.value.forEach(player => {
    const tier = player.tier || 'UNRANKED'
    tiers[tier] = (tiers[tier] || 0) + 1
  })
  
  return Object.entries(tiers).map(([name, count]) => ({ name, count }))
})

// 메서드
const handleWebSocketMessage = (data) => {
  switch (data.type) {
    case 'balance_analysis_complete':
      teamComposition.value = data.teamComposition
      aiAnalysis.value = data.aiAnalysis
      isAnalyzing.value = false
      break
    case 'match_status_update':
      refreshData()
      break
  }
}

const fetchActiveMatches = async () => {
  try {
    loading.value = true
    const response = await fetch(`${API_BASE_URL}/matches/realtime`)
    
    if (response.ok) {
      const data = await response.json()
      activeMatches.value = data.matches.filter(match => 
        match.status === 'open' || match.status === 'in_progress'
      )
    }
  } catch (error) {
    console.error('활성 내전 조회 실패:', error)
  } finally {
    loading.value = false
  }
}

const selectMatch = (match) => {
  selectedMatch.value = match
  players.value = []
  teamComposition.value = null
  aiAnalysis.value = ''
}

const addPlayer = async () => {
  if (!newPlayer.value.gameName || !newPlayer.value.tagLine) return

  const player = {
    gameName: newPlayer.value.gameName,
    tagLine: newPlayer.value.tagLine,
    preferredRole: newPlayer.value.preferredRole || 'FILL',
    loading: true,
    tier: '',
    rank: '',
    lp: 0,
    score: 0,
    championMasteries: [],
    assignedRole: '',
    isTeamLeader: false
  }

  players.value.push(player)
  newPlayer.value = { gameName: '', tagLine: '', preferredRole: '' }

  // Riot API로 플레이어 정보 조회
  try {
    const response = await fetch(`${API_BASE_URL}/riot/player/${player.gameName}/${player.tagLine}`)
    if (response.ok) {
      const data = await response.json()
      const league = data.league?.[0]
      player.tier = league?.tier || 'UNRANKED'
      player.rank = league?.rank || 'IV'
      player.lp = league?.leaguePoints || 0
      player.championMasteries = data.champion_masteries || []
      player.score = calculatePlayerScore(data)
      player.loading = false
    } else {
      player.tier = 'UNRANKED'
      player.rank = 'IV'
      player.lp = 0
      player.score = 0
      player.loading = false
    }
  } catch (error) {
    console.error('플레이어 정보 조회 실패:', error)
    player.tier = 'UNRANKED'
    player.rank = 'IV'
    player.lp = 0
    player.score = 0
    player.loading = false
  }
}

const calculatePlayerScore = (playerData) => {
  const tierScores = {
    'IRON': 100, 'BRONZE': 200, 'SILVER': 300, 'GOLD': 400,
    'PLATINUM': 500, 'DIAMOND': 600, 'MASTER': 700, 'GRANDMASTER': 800, 'CHALLENGER': 900
  }
  
  const league = playerData.league?.[0]
  if (!league) return 0
  
  const baseScore = tierScores[league.tier] || 0
  const rankBonus = { 'I': 75, 'II': 50, 'III': 25, 'IV': 0 }[league.rank] || 0
  const lpBonus = Math.floor(league.leaguePoints / 10)
  
  // 챔피언 마스터리 보너스 (상위 3개 챔피언 평균 점수 × 0.1)
  let masteryBonus = 0
  if (playerData.champion_masteries && playerData.champion_masteries.length > 0) {
    const top3Masteries = playerData.champion_masteries.slice(0, 3)
    const avgMastery = top3Masteries.reduce((sum, mastery) => sum + mastery.championPoints, 0) / top3Masteries.length
    masteryBonus = Math.floor(avgMastery * 0.1)
  }
  
  return baseScore + rankBonus + lpBonus + masteryBonus
}

const removePlayer = (index) => {
  players.value.splice(index, 1)
  teamComposition.value = null
  aiAnalysis.value = ''
}

const startAnalysis = async () => {
  if (players.value.length < 2) {
    alert('최소 2명의 플레이어가 필요합니다.')
    return
  }

  isAnalyzing.value = true
  teamComposition.value = null
  aiAnalysis.value = ''

  try {
    // 팀 밸런스 계산
    const composition = calculateTeamBalance(players.value)
    teamComposition.value = composition

    // AI 분석 요청
    const analysisResponse = await fetch(`${API_BASE_URL}/ai/analyze-balance`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ players: players.value, composition })
    })

    if (analysisResponse.ok) {
      const analysisData = await analysisResponse.json()
      aiAnalysis.value = analysisData.analysis
    }

    // WebSocket으로 결과 전송
    send({
      type: 'balance_analysis_complete',
      matchId: selectedMatch.value.id,
      teamComposition: composition,
      aiAnalysis: aiAnalysis.value
    })

  } catch (error) {
    console.error('밸런스 분석 실패:', error)
    alert('밸런스 분석에 실패했습니다.')
  } finally {
    isAnalyzing.value = false
  }
}

const calculateTeamBalance = (players) => {
  // 라인별로 플레이어 분류
  const roleGroups = {
    'TOP': [],
    'JUNGLE': [],
    'MID': [],
    'ADC': [],
    'SUPPORT': []
  }

  // 플레이어를 선호 라인별로 분류
  players.forEach(player => {
    const role = player.preferredRole || 'FILL'
    if (roleGroups[role]) {
      roleGroups[role].push(player)
    } else {
      // FILL인 경우 가장 적은 라인에 배치
      const minRole = Object.keys(roleGroups).reduce((min, key) => 
        roleGroups[key].length < roleGroups[min].length ? key : min
      )
      roleGroups[minRole].push(player)
    }
  })

  // 각 라인별로 점수순 정렬
  Object.keys(roleGroups).forEach(role => {
    roleGroups[role].sort((a, b) => b.score - a.score)
  })

  // 팀 분배 (라인별 밸런스 고려)
  const team1 = []
  const team2 = []
  let team1Score = 0
  let team2Score = 0

  // 각 라인에서 최고 점수 플레이어를 팀에 배치
  Object.keys(roleGroups).forEach(role => {
    const rolePlayers = roleGroups[role]
    if (rolePlayers.length === 0) return

    // 라인별로 팀 분배
    for (let i = 0; i < rolePlayers.length; i++) {
      const player = rolePlayers[i]
      const playerData = {
        name: `${player.gameName}#${player.tagLine}`,
        tier: player.tier,
        rank: player.rank,
        lp: player.lp,
        score: player.score,
        role: role,
        isTeamLeader: false
      }

      if (i % 2 === 0) {
        team1.push(playerData)
        team1Score += playerData.score
      } else {
        team2.push(playerData)
        team2Score += playerData.score
      }
    }
  })

  // 팀장 지정 (각 팀에서 가장 높은 점수 플레이어)
  if (team1.length > 0) {
    const team1Leader = team1.reduce((max, player) => 
      player.score > max.score ? player : max
    )
    team1Leader.isTeamLeader = true
  }

  if (team2.length > 0) {
    const team2Leader = team2.reduce((max, player) => 
      player.score > max.score ? player : max
    )
    team2Leader.isTeamLeader = true
  }

  const balanceScore = Math.abs(team1Score - team2Score)

  return {
    team1,
    team2,
    team1Score,
    team2Score,
    balanceScore,
    isBalanced: balanceScore < 200,
    roleDistribution: Object.keys(roleGroups).map(role => ({
      role,
      count: roleGroups[role].length,
      players: roleGroups[role].map(p => `${p.gameName}#${p.tagLine}`)
    }))
  }
}

const resetAnalysis = () => {
  players.value = []
  teamComposition.value = null
  aiAnalysis.value = ''
  newPlayer.value = { gameName: '', tagLine: '' }
}

const refreshData = () => {
  fetchActiveMatches()
}

const getStatusText = (status) => {
  const statusMap = {
    'open': '모집중',
    'in_progress': '진행중',
    'completed': '완료',
    'closed': '종료'
  }
  return statusMap[status] || status
}

const getTypeText = (type) => {
  const typeMap = {
    'soft': '소프트',
    'hard': '하드',
    'hyper': '하이퍼'
  }
  return typeMap[type] || type
}

const getBalanceClass = (score) => {
  if (score < 100) return 'excellent'
  if (score < 200) return 'good'
  if (score < 300) return 'fair'
  return 'poor'
}

const getBarWidth = (value, maxValue) => {
  const max = Math.max(value, maxValue)
  return max > 0 ? `${(value / max) * 100}%` : '0%'
}

const getRoleText = (role) => {
  const roleMap = {
    'TOP': '탑',
    'JUNGLE': '정글',
    'MID': '미드',
    'ADC': '원딜',
    'SUPPORT': '서포터',
    'FILL': '자동'
  }
  return roleMap[role] || role
}

// 라이프사이클
onMounted(() => {
  fetchActiveMatches()
})
</script>

<style scoped>
.balance-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.balance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-radius: 15px;
  backdrop-filter: blur(10px);
}

.balance-header h1 {
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

.match-selection, .balance-analysis {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 25px;
  margin-bottom: 25px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.match-selection h2, .balance-analysis h3 {
  color: #333;
  margin-bottom: 20px;
  font-size: 1.5rem;
  font-weight: bold;
}

.no-matches {
  text-align: center;
  padding: 40px;
  color: #666;
}

.no-matches-icon {
  font-size: 3rem;
  margin-bottom: 15px;
}

.matches-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
}

.match-card {
  background: white;
  border-radius: 10px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.match-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.match-card.active {
  border-color: #667eea;
  background: #f0f4ff;
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

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.analysis-controls {
  display: flex;
  gap: 10px;
}

.analyze-btn, .reset-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.analyze-btn {
  background: #4CAF50;
  color: white;
}

.analyze-btn:hover:not(:disabled) {
  background: #45a049;
}

.analyze-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.reset-btn {
  background: #f44336;
  color: white;
}

.reset-btn:hover {
  background: #da190b;
}

.player-input-section {
  margin-bottom: 30px;
}

.player-input-section h4 {
  margin-bottom: 15px;
  color: #333;
}

.player-input {
  display: flex;
  gap: 10px;
  align-items: center;
}

.player-input-field {
  flex: 1;
  padding: 10px 15px;
  border: 2px solid #e0e0e0;
  border-radius: 25px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s ease;
}

.player-input-field:focus {
  border-color: #667eea;
}

.add-player-btn {
  padding: 10px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.add-player-btn:hover:not(:disabled) {
  background: #5a6fd8;
}

.add-player-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.players-section {
  margin-bottom: 30px;
}

.players-section h4 {
  margin-bottom: 15px;
  color: #333;
}

.no-players {
  text-align: center;
  padding: 40px;
  color: #666;
  background: #f8f9fa;
  border-radius: 10px;
}

.players-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.player-card {
  background: white;
  border-radius: 10px;
  padding: 15px;
  border: 2px solid #e0e0e0;
  transition: all 0.3s ease;
}

.player-card.loading {
  opacity: 0.6;
}

.player-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.player-info {
  margin-bottom: 10px;
}

.player-name {
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.player-tier {
  color: #667eea;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.player-score {
  color: #666;
  font-size: 0.8rem;
}

.player-actions {
  display: flex;
  justify-content: flex-end;
}

.remove-btn {
  background: #f44336;
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s ease;
}

.remove-btn:hover {
  background: #da190b;
  transform: scale(1.1);
}

.team-composition {
  margin-bottom: 30px;
}

.team-composition h4 {
  margin-bottom: 20px;
  color: #333;
}

.balance-summary {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 10px;
}

.balance-score, .balance-status {
  display: flex;
  align-items: center;
  gap: 10px;
}

.balance-score .label, .balance-status .label {
  font-weight: bold;
  color: #333;
}

.balance-score .value {
  font-size: 1.2rem;
  font-weight: bold;
}

.balance-score .value.excellent {
  color: #4CAF50;
}

.balance-score .value.good {
  color: #8BC34A;
}

.balance-score .value.fair {
  color: #FF9800;
}

.balance-score .value.poor {
  color: #f44336;
}

.balance-status .value.balanced {
  color: #4CAF50;
}

.balance-status .value.unbalanced {
  color: #f44336;
}

.teams-display {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.team {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
}

.team h5 {
  margin-bottom: 10px;
  color: #333;
}

.team-score {
  font-weight: bold;
  color: #667eea;
  margin-bottom: 15px;
}

.team-players {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.team-player {
  background: white;
  border-radius: 8px;
  padding: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.team-player .player-name {
  font-weight: bold;
  color: #333;
}

.team-player .player-tier {
  color: #667eea;
  font-size: 0.9rem;
}

.team-player .player-score {
  color: #666;
  font-size: 0.8rem;
}

.ai-analysis {
  margin-bottom: 30px;
}

.ai-analysis h4 {
  margin-bottom: 15px;
  color: #333;
}

.analysis-content {
  background: #f0f4ff;
  border-radius: 10px;
  padding: 20px;
  border-left: 4px solid #667eea;
}

.analysis-text {
  color: #333;
  line-height: 1.6;
  white-space: pre-wrap;
}

.visualization {
  margin-bottom: 30px;
}

.visualization h4 {
  margin-bottom: 20px;
  color: #333;
}

.charts-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.chart {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.chart h5 {
  margin-bottom: 15px;
  color: #333;
  text-align: center;
}

.score-chart {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.chart-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.bar-label {
  width: 60px;
  font-weight: bold;
  color: #333;
}

.bar-container {
  flex: 1;
  height: 20px;
  background: #e0e0e0;
  border-radius: 10px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  transition: width 0.5s ease;
}

.bar-fill.blue {
  background: linear-gradient(90deg, #2196F3, #21CBF3);
}

.bar-fill.red {
  background: linear-gradient(90deg, #f44336, #ff7043);
}

.bar-value {
  width: 40px;
  text-align: right;
  font-weight: bold;
  color: #333;
}

.tier-distribution {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tier-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.tier-name {
  font-weight: bold;
  color: #333;
}

.tier-count {
  color: #667eea;
  font-weight: bold;
}

@media (max-width: 768px) {
  .teams-display {
    grid-template-columns: 1fr;
  }
  
  .charts-container {
    grid-template-columns: 1fr;
  }
  
  .balance-summary {
    flex-direction: column;
    gap: 15px;
  }
  
  .player-input {
    flex-direction: column;
  }
  
  .players-grid {
    grid-template-columns: 1fr;
  }
}

/* 티어 점수 기준표 스타일 */
.tier-score-guide {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 30px;
  border-left: 4px solid #667eea;
}

.tier-score-guide h4 {
  margin-bottom: 15px;
  color: #333;
}

.score-guide-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.tier-scores {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
}

.tier-score-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.tier-name {
  font-weight: bold;
  color: #333;
}

.tier-score {
  color: #667eea;
  font-weight: bold;
}

.score-details {
  background: white;
  border-radius: 6px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.score-details p {
  margin-bottom: 10px;
  color: #333;
  font-weight: bold;
}

.score-details ul {
  margin: 0;
  padding-left: 20px;
  color: #666;
  font-size: 0.9rem;
}

.score-details li {
  margin-bottom: 5px;
}

/* 라인 선택 스타일 */
.role-select {
  padding: 10px 15px;
  border: 2px solid #e0e0e0;
  border-radius: 25px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s ease;
  background: white;
}

.role-select:focus {
  border-color: #667eea;
}

/* 플레이어 카드 개선 */
.player-details {
  margin: 5px 0;
}

.player-tier {
  color: #667eea;
  font-size: 0.9rem;
  margin-bottom: 2px;
}

.player-lp {
  color: #666;
  font-size: 0.8rem;
  margin-bottom: 2px;
}

.player-role {
  color: #4CAF50;
  font-size: 0.8rem;
  font-weight: bold;
  background: #e8f5e8;
  padding: 2px 6px;
  border-radius: 10px;
  display: inline-block;
}

/* 팀 플레이어 개선 */
.team-player {
  background: white;
  border-radius: 8px;
  padding: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.team-player.team-leader {
  border-color: #FFD700;
  background: linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%);
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.2);
}

.team-player .player-info {
  flex: 1;
}

.team-player .player-name {
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.leader-badge {
  font-size: 1.2rem;
  animation: crownGlow 2s ease-in-out infinite;
}

@keyframes crownGlow {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.team-player .player-role {
  color: #667eea;
  font-size: 0.8rem;
  font-weight: bold;
  background: #e3f2fd;
  padding: 2px 6px;
  border-radius: 10px;
  display: inline-block;
}

.team-player .player-stats {
  text-align: right;
}

.team-player .player-tier {
  color: #666;
  font-size: 0.8rem;
  margin-bottom: 2px;
}

.team-player .player-score {
  color: #333;
  font-weight: bold;
  font-size: 0.9rem;
}

/* 라인 분포 스타일 */
.role-distribution {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 10px;
}

.role-distribution h5 {
  margin-bottom: 15px;
  color: #333;
}

.role-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
}

.role-stat {
  background: white;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.role-name {
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.role-count {
  color: #667eea;
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 5px;
}

.role-players {
  color: #666;
  font-size: 0.8rem;
  line-height: 1.3;
}

@media (max-width: 768px) {
  .score-guide-content {
    grid-template-columns: 1fr;
  }
  
  .tier-scores {
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  }
  
  .role-stats {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  }
  
  .team-player {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .team-player .player-stats {
    text-align: left;
    width: 100%;
  }
}
</style>
