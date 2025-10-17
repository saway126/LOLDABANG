<template>
  <div class="balance">
    <div class="page-header">
      <h2 class="page-title">⚖️ 밸런스 조율</h2>
      <p class="page-subtitle">공정한 팀 구성을 위한 밸런싱 도구입니다</p>
    </div>
    
    <div class="form-container">
      <div class="form-section">
        <h3 class="section-title">🏆 내전 선택</h3>
        <div class="match-selection">
          <div class="match-grid">
            <button 
              v-for="match in matches" 
              :key="match.id"
              @click="selectMatch(match.id)"
              :class="['match-card', { active: selectedMatchId === match.id }]"
            >
              <div class="match-icon">🎮</div>
              <div class="match-info">
                <div class="match-id">{{ match.customId }}</div>
                <div class="match-details">{{ match.type }} • {{ match.host }}</div>
              </div>
            </button>
          </div>
        </div>
      </div>
      
      <div v-if="participants.length > 0" class="form-section">
        <h3 class="section-title">👥 참가자 선택</h3>
        <div class="participants-container">
          <div class="participants-header">
            <span class="participants-count">{{ selectedParticipantIds.length }}명 선택됨</span>
            <button 
              type="button" 
              @click="toggleSelectAllParticipants"
              class="select-all-btn"
            >
              <span class="btn-icon">{{ selectedParticipantIds.length === participants.length ? '☑️' : '☐' }}</span>
              <span class="btn-text">{{ selectedParticipantIds.length === participants.length ? '전체 해제' : '전체 선택' }}</span>
            </button>
          </div>
          
          <div class="player-grid">
            <div 
              v-for="player in participants" 
              :key="player.id"
              class="player-card"
              :class="{ 'selected': selectedParticipantIds.includes(player.id!) }"
              @click="toggleParticipant(player.id!)"
            >
              <div class="player-checkbox">
                {{ selectedParticipantIds.includes(player.id!) ? '☑️' : '☐' }}
              </div>
              <div class="player-info">
                <div class="player-name">{{ player.name }}</div>
                <div class="player-details">
                  <span :class="['tier-badge', getTierClass(player.tier)]">
                    {{ player.tier || 'UNRANKED' }}{{ player.rank || '' }}
                  </span>
                  <span class="lane-info">
                    <span class="main-lane">
                      {{ getLaneIcon(player.mainLane) }} {{ player.mainLane || 'UNKNOWN' }}
                    </span>
                    <span v-if="player.preferredLanes && player.preferredLanes.length > 0" class="preferred-lanes">
                      (희망: {{ player.preferredLanes.join(', ') }})
                    </span>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="form-actions">
        <button 
          @click="runBalance"
          :disabled="loading || selectedParticipantIds.length < 10"
          class="balance-btn"
        >
          <span class="btn-icon">{{ loading ? '⏳' : '⚖️' }}</span>
          <span class="btn-text">{{ loading ? '밸런싱 중...' : '밸런싱 실행' }}</span>
        </button>
        
        <button 
          @click="runBalance"
          :disabled="!balanceResult || loading"
          class="balance-btn"
        >
          다시짜기
        </button>
      </div>
      
      <div v-if="balanceResult" class="balance-result">
        <div class="result-header">
          <h3 class="result-title">🎯 밸런싱 결과</h3>
          <div class="quality-score">
            <span class="quality-label">품질 점수</span>
            <span :class="['quality-value', getQualityClass(balanceResult.qualityScore)]">
              {{ (balanceResult.qualityScore * 100).toFixed(1) }}%
            </span>
          </div>
        </div>
        
        <div class="teams-container">
          <div 
            v-for="(team, index) in balanceResult.teams" 
            :key="index"
            class="team-card"
          >
            <div class="team-header">
              <h4 class="team-title">팀 {{ index + 1 }}</h4>
              <div class="team-score">점수: {{ team.totalScore.toFixed(1) }}</div>
            </div>
            <div class="team-players">
              <div 
                v-for="(player, playerIndex) in team.players" 
                :key="playerIndex"
                :class="['team-player', { 'captain': isCaptain(index, playerIndex) }]"
                @click="selectCaptain(index, playerIndex)"
              >
                <div class="captain-selector">
                  <span v-if="isCaptain(index, playerIndex)" class="captain-badge">👑</span>
                  <span v-else class="captain-select">선택</span>
                </div>
                <div class="player-info">
                  <div class="player-name">{{ player.name }}</div>
                  <div class="player-details">
                    <span :class="['tier-badge', getTierClass(player.tier)]">
                      {{ player.tier || 'UNRANKED' }}{{ player.rank || '' }}
                    </span>
                    <span class="lane-info">
                      <span class="main-lane">
                        {{ getLaneIcon(player.mainLane) }} {{ player.mainLane || 'UNKNOWN' }}
                      </span>
                      <span v-if="player.preferredLanes && player.preferredLanes.length > 0" class="preferred-lanes">
                        (희망: {{ player.preferredLanes.join(', ') }})
                      </span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Player {
  id?: number
  name: string
  tier: string
  rank: string
  mainLane: string
  preferredLanes: string[]
}

interface Match {
  id: number
  customId: string
  host: string
  type: string
  status: string
  createdAt: string
}

interface BalanceResult {
  teams: Array<{
    players: Player[]
    totalScore: number
  }>
  qualityScore: number
}

const matches = ref<Match[]>([])
const participants = ref<Player[]>([])
const selectedMatchId = ref<number | null>(null)
const selectedParticipantIds = ref<number[]>([])
const loading = ref(false)
const balanceResult = ref<BalanceResult | null>(null)
const teamCaptains = ref<Record<string, number>>({})

// 환경에 따라 API URL 설정
const API_BASE_URL = import.meta.env.DEV 
  ? 'http://localhost:4000/api' 
  : 'https://backend-gra76l5e2-skwka12346-gmailcoms-projects.vercel.app/api'

const fetchMatches = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/matches/recent`)
    const data = await response.json()
    matches.value = data
  } catch (error) {
    console.error('Failed to fetch matches:', error)
    matches.value = []
  }
}

const selectMatch = async (matchId: number) => {
  selectedMatchId.value = matchId
  try {
    const response = await fetch(`${API_BASE_URL}/matches/${matchId}/participants`)
    const data = await response.json()
    participants.value = data
    selectedParticipantIds.value = []
    balanceResult.value = null
    teamCaptains.value = {}
  } catch (error) {
    console.error('Failed to fetch participants:', error)
    participants.value = []
  }
}

const toggleParticipant = (playerId: number) => {
  const index = selectedParticipantIds.value.indexOf(playerId)
  if (index > -1) {
    selectedParticipantIds.value.splice(index, 1)
  } else {
    selectedParticipantIds.value.push(playerId)
  }
}

const toggleSelectAllParticipants = () => {
  if (selectedParticipantIds.value.length === participants.value.length) {
    selectedParticipantIds.value = []
  } else {
    selectedParticipantIds.value = participants.value.map(p => p.id!).filter(id => id !== undefined)
  }
}

const runBalance = async () => {
  if (selectedParticipantIds.value.length < 10) {
    alert('최소 10명의 참가자를 선택해주세요.')
    return
  }

  loading.value = true
  
  try {
    const selectedPlayers = participants.value.filter(p => 
      selectedParticipantIds.value.includes(p.id!)
    )
    
    // 간단한 밸런싱 알고리즘 (그리디)
    const shuffled = [...selectedPlayers].sort(() => Math.random() - 0.5)
    const team1: Player[] = []
    const team2: Player[] = []
    
    // 라인별로 분배
    const team1Lanes = new Set<string>()
    const team2Lanes = new Set<string>()
    
    for (const player of shuffled) {
      const mainLane = player.mainLane
      
      if (team1Lanes.has(mainLane) && !team2Lanes.has(mainLane)) {
        team2.push(player)
        team2Lanes.add(mainLane)
      } else if (team2Lanes.has(mainLane) && !team1Lanes.has(mainLane)) {
        team1.push(player)
        team1Lanes.add(mainLane)
      } else if (team1.length <= team2.length) {
        team1.push(player)
        team1Lanes.add(mainLane)
      } else {
        team2.push(player)
        team2Lanes.add(mainLane)
      }
    }
    
    // 점수 계산 (간단한 예시)
    const calculateScore = (players: Player[]) => {
      return players.reduce((sum, player) => {
        const tierScores: Record<string, number> = {
          'CHALLENGER': 10, 'GRANDMASTER': 9, 'MASTER': 8,
          'DIAMOND': 7, 'PLATINUM': 6, 'GOLD': 5,
          'SILVER': 4, 'BRONZE': 3, 'IRON': 2, 'UNRANKED': 1
        }
        return sum + (tierScores[player.tier] || 1)
      }, 0)
    }
    
    const team1Score = calculateScore(team1)
    const team2Score = calculateScore(team2)
    const totalScore = team1Score + team2Score
    const qualityScore = 1 - Math.abs(team1Score - team2Score) / totalScore
    
    balanceResult.value = {
      teams: [
        { players: team1, totalScore: team1Score },
        { players: team2, totalScore: team2Score }
      ],
      qualityScore
    }
    
    // 팀장 초기화
    teamCaptains.value = {}
  } catch (error) {
    console.error('Balance error:', error)
    alert('밸런싱 중 오류가 발생했습니다.')
  } finally {
    loading.value = false
  }
}

const selectCaptain = (teamIndex: number, playerIndex: number) => {
  const teamKey = `team${teamIndex}`
  teamCaptains.value[teamKey] = playerIndex
}

const isCaptain = (teamIndex: number, playerIndex: number): boolean => {
  const teamKey = `team${teamIndex}`
  return teamCaptains.value[teamKey] === playerIndex
}

const getTierClass = (tier: string): string => {
  if (!tier) return 'tier-unranked'
  return `tier-${tier.toLowerCase()}`
}

const getLaneIcon = (lane: string): string => {
  const icons: Record<string, string> = {
    'TOP': '🏔️',
    'JUNGLE': '🌲',
    'MID': '⚔️',
    'ADC': '🏹',
    'SUPPORT': '🛡️',
    'UNKNOWN': '❓'
  }
  return icons[lane] || '❓'
}

const getQualityClass = (score: number): string => {
  if (score >= 0.8) return 'quality-good'
  if (score >= 0.6) return 'quality-medium'
  return 'quality-poor'
}

onMounted(() => {
  fetchMatches()
})
</script>

<style scoped>
.balance {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.page-header {
  text-align: center;
  margin-bottom: 2rem;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(139, 69, 19, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(212, 196, 168, 0.3);
}

.page-title {
  color: #8B4513;
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: bold;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
}

.page-subtitle {
  color: #A0522D;
  margin: 0;
  font-size: 1rem;
  opacity: 0.8;
}

.form-container {
  background: rgba(255, 255, 255, 0.9);
  padding: 2rem;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(139, 69, 19, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(212, 196, 168, 0.3);
}

.form-section {
  margin-bottom: 2.5rem;
}

.section-title {
  color: #8B4513;
  margin: 0 0 1.5rem 0;
  font-size: 1.3rem;
  font-weight: bold;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
  border-bottom: 2px solid #d4c4a8;
  padding-bottom: 0.5rem;
}

.match-selection {
  background: rgba(245, 241, 232, 0.5);
  padding: 1.5rem;
  border-radius: 15px;
  border: 1px solid rgba(212, 196, 168, 0.3);
}

.match-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.match-card {
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid #d4c4a8;
  border-radius: 12px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 1rem;
  text-align: left;
}

.match-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 69, 19, 0.2);
  border-color: #8B4513;
}

.match-card.active {
  background: rgba(139, 69, 19, 0.1);
  border-color: #8B4513;
  box-shadow: 0 4px 12px rgba(139, 69, 19, 0.2);
}

.match-icon {
  font-size: 1.5rem;
  color: #8B4513;
}

.match-info {
  flex: 1;
}

.match-id {
  font-weight: bold;
  color: #8B4513;
  font-size: 1rem;
  margin-bottom: 0.2rem;
}

.match-details {
  font-size: 0.85rem;
  color: #A0522D;
  opacity: 0.8;
}

.participants-container {
  background: rgba(245, 241, 232, 0.5);
  padding: 1.5rem;
  border-radius: 15px;
  border: 1px solid rgba(212, 196, 168, 0.3);
}

.participants-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(212, 196, 168, 0.5);
}

.participants-count {
  color: #8B4513;
  font-weight: bold;
  font-size: 1.1rem;
}

.select-all-btn {
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid #d4c4a8;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  color: #8B4513;
  font-weight: 500;
}

.select-all-btn:hover {
  background: rgba(139, 69, 19, 0.1);
  border-color: #8B4513;
}

.player-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  max-height: 400px;
  overflow-y: auto;
  padding: 0.5rem;
}

.player-card {
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid #d4c4a8;
  border-radius: 12px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.player-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 69, 19, 0.2);
  border-color: #8B4513;
}

.player-card.selected {
  background: rgba(139, 69, 19, 0.1);
  border-color: #8B4513;
  box-shadow: 0 4px 12px rgba(139, 69, 19, 0.2);
}

.player-checkbox {
  font-size: 1.2rem;
  color: #8B4513;
}

.player-info {
  flex: 1;
}

.player-name {
  font-weight: bold;
  color: #8B4513;
  margin-bottom: 0.3rem;
  font-size: 1rem;
}

.player-details {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.tier-badge {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: bold;
  color: white;
  margin-right: 0.5rem;
}

.tier-iron { background: #8B4513; }
.tier-bronze { background: #CD7F32; }
.tier-silver { background: #C0C0C0; color: #333; }
.tier-gold { background: #FFD700; color: #333; }
.tier-platinum { background: #00CED1; }
.tier-diamond { background: #B9F2FF; color: #333; }
.tier-master { background: #8A2BE2; }
.tier-grandmaster { background: #FF4500; }
.tier-challenger { background: #FFD700; color: #333; }
.tier-unranked { background: #666; }

.lane-info {
  font-size: 0.85rem;
  color: #A0522D;
}

.main-lane {
  font-weight: 500;
  margin-right: 0.5rem;
}

.preferred-lanes {
  font-size: 0.8rem;
  color: #8B4513;
  opacity: 0.7;
}

.form-actions {
  text-align: center;
  margin: 2rem 0;
  padding: 2rem 0;
  border-top: 1px solid rgba(212, 196, 168, 0.5);
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.balance-btn {
  background: linear-gradient(135deg, #8B4513, #A0522D);
  color: white;
  border: none;
  padding: 1.2rem 3rem;
  border-radius: 15px;
  cursor: pointer;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  box-shadow: 0 6px 20px rgba(139, 69, 19, 0.3);
}

.balance-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(139, 69, 19, 0.4);
}

.balance-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-icon {
  font-size: 1.1rem;
}

.btn-text {
  font-weight: 500;
}

.balance-result {
  margin-top: 2rem;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(139, 69, 19, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(212, 196, 168, 0.3);
}

.result-header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid #d4c4a8;
}

.result-title {
  color: #8B4513;
  margin: 0 0 1rem 0;
  font-size: 1.5rem;
  font-weight: bold;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
}

.quality-score {
  background: rgba(245, 241, 232, 0.8);
  padding: 1rem 2rem;
  border-radius: 15px;
  display: inline-flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid rgba(212, 196, 168, 0.5);
}

.quality-label {
  font-weight: bold;
  color: #8B4513;
  font-size: 1rem;
}

.quality-value {
  font-size: 1.3rem;
  font-weight: bold;
  padding: 0.5rem 1rem;
  border-radius: 10px;
}

.quality-good {
  color: #4CAF50;
  background: rgba(76, 175, 80, 0.1);
}

.quality-medium {
  color: #FF9800;
  background: rgba(255, 152, 0, 0.1);
}

.quality-poor {
  color: #f44336;
  background: rgba(244, 67, 54, 0.1);
}

.teams-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.team-card {
  background: rgba(245, 241, 232, 0.5);
  border: 2px solid #d4c4a8;
  border-radius: 15px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.team-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(139, 69, 19, 0.2);
}

.team-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(212, 196, 168, 0.5);
}

.team-title {
  color: #8B4513;
  margin: 0;
  font-size: 1.2rem;
  font-weight: bold;
}

.team-score {
  color: #A0522D;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.8);
  padding: 0.3rem 0.8rem;
  border-radius: 8px;
}

.team-players {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.team-player {
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid #d4c4a8;
  border-radius: 12px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.team-player:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(139, 69, 19, 0.2);
  border-color: #8B4513;
}

.team-player.captain {
  background: rgba(255, 193, 7, 0.2);
  border-color: #ffc107;
  box-shadow: 0 4px 12px rgba(255, 193, 7, 0.3);
}

.captain-selector {
  min-width: 60px;
  text-align: center;
}

.captain-badge {
  font-size: 1.5rem;
  color: #ffc107;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

.captain-select {
  font-size: 0.8rem;
  color: #8B4513;
  padding: 0.3rem 0.6rem;
  background: rgba(139, 69, 19, 0.1);
  border-radius: 6px;
  font-weight: 500;
}

.team-player.captain .captain-select {
  background: #ffc107;
  color: #8B4513;
  font-weight: bold;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .match-grid {
    grid-template-columns: 1fr;
  }
  
  .player-grid {
    grid-template-columns: 1fr;
  }
  
  .teams-container {
    grid-template-columns: 1fr;
  }
  
  .participants-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .form-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .form-container {
    padding: 1.5rem;
  }
}
</style>