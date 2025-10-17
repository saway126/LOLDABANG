<template>
  <div class="balance">
    <h2>밸런스 조율</h2>
    
    <div class="form">
      <div class="form-group">
        <label>내전 선택</label>
        <div class="match-list">
          <button 
            v-for="match in matches" 
            :key="match.id"
            @click="selectMatch(match.id)"
            :class="['match-btn', { active: selectedMatchId === match.id }]"
          >
            {{ match.customId }}
          </button>
        </div>
      </div>
      
      <div v-if="participants.length > 0" class="form-group">
        <label>참가자 선택 ({{ selectedParticipantIds.length }}명 선택됨)</label>
        <div class="player-list">
          <button 
            type="button" 
            @click="toggleSelectAllParticipants"
            class="select-all-btn"
          >
            {{ selectedParticipantIds.length === participants.length ? '전체 해제' : '전체 선택' }}
          </button>
          
          <div 
            v-for="player in participants" 
            :key="player.id"
            class="player-item"
            @click="toggleParticipant(player.id!)"
          >
            <span class="checkbox">
              {{ selectedParticipantIds.includes(player.id!) ? '☑️' : '☐' }}
            </span>
            <span class="player-text">
              <span class="player-name">{{ player.name }}</span>
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
            </span>
          </div>
        </div>
      </div>
      
      <div class="button-row">
        <button 
          @click="runBalance"
          :disabled="loading || selectedParticipantIds.length < 10"
          class="balance-btn"
        >
          {{ loading ? '밸런싱 중...' : '밸런싱 실행' }}
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
        <div class="quality-score">
          <span class="quality-label">품질 점수:</span>
          <span :class="['quality-value', getQualityClass(balanceResult.qualityScore)]">
            {{ (balanceResult.qualityScore * 100).toFixed(1) }}%
          </span>
        </div>
        
        <div 
          v-for="(team, index) in balanceResult.teams" 
          :key="index"
          class="team-card"
        >
          <h4>팀 {{ index + 1 }} (점수: {{ team.totalScore.toFixed(1) }})</h4>
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
            <span class="player-name">{{ player.name }}</span>
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
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'

interface Match {
  id: number
  customId: string
}

interface Player {
  id?: number
  name: string
  tier?: string
  rank?: string
  mainLane?: string
  preferredLanes?: string[]
  mmr?: number
}

interface Team {
  players: Player[]
  totalScore: number
  lanes: Record<string, Player | null>
}

interface BalanceResult {
  teams: Team[]
  qualityScore: number
}

const loading = ref(false)
const matches = ref<Match[]>([])
const selectedMatchId = ref<number | null>(null)
const participants = ref<Player[]>([])
const selectedParticipantIds = ref<number[]>([])
const balanceResult = ref<BalanceResult | null>(null)
const teamCaptains = ref<Record<number, number>>({})

const API_BASE_URL = 'http://localhost:4000/api'

const balanceTeams = (players: Player[], options: { teamSize: number }): BalanceResult => {
  const { teamSize = 5 } = options
  const numTeams = Math.floor(players.length / teamSize)
  
  if (numTeams < 2) {
    return { teams: [], qualityScore: 0 }
  }

  const TIER_SCORES: Record<string, number> = {
    IRON: 1, I: 1,
    BRONZE: 2, B: 2,
    SILVER: 3, S: 3,
    GOLD: 4, G: 4,
    PLATINUM: 5, P: 5,
    EMERALD: 6, E: 6,
    DIAMOND: 7, D: 7,
    MASTER: 8, M: 8,
    GRANDMASTER: 9, GM: 9,
    CHALLENGER: 10, C: 10,
    UNRANKED: 3,
  }

  const getPlayerScore = (player: Player): number => {
    if (player.mmr) return player.mmr
    const tierScore = TIER_SCORES[player.tier?.toUpperCase() || 'UNRANKED'] || 3
    const rankScore = player.rank ? (5 - parseInt(player.rank, 10)) * 0.2 : 0
    return tierScore + rankScore
  }

  const scoredPlayers = players.map(p => ({ ...p, score: getPlayerScore(p) }))
    .sort((a, b) => b.score - a.score)

  const teams: Team[] = Array.from({ length: numTeams }, () => ({ 
    players: [], 
    totalScore: 0, 
    lanes: {} 
  }))

  scoredPlayers.forEach(player => {
    const teamWithLowestScore = teams.sort((a, b) => a.totalScore - b.totalScore)[0]
    teamWithLowestScore.players.push(player)
    teamWithLowestScore.totalScore += player.score
  })

  const totalScores = teams.map(t => t.totalScore)
  const minScore = Math.min(...totalScores)
  const maxScore = Math.max(...totalScores)
  const qualityScore = 1 - (maxScore - minScore) / (maxScore || 1)

  return { teams, qualityScore }
}

const fetchMatches = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/matches/recent`)
    const data = await response.json()
    matches.value = data
  } catch (error) {
    console.error('Failed to fetch matches:', error)
  }
}

const fetchParticipants = async (matchId: number) => {
  try {
    const response = await fetch(`${API_BASE_URL}/matches/${matchId}/participants`)
    const data = await response.json()
    console.log('Fetched participants:', data) // 디버깅용
    participants.value = data
    selectedParticipantIds.value = data.map((p: Player) => p.id!).filter(Boolean)
  } catch (error) {
    console.error('Failed to fetch participants:', error)
  }
}

const selectMatch = (matchId: number) => {
  selectedMatchId.value = matchId
  fetchParticipants(matchId)
  balanceResult.value = null
}

const toggleSelectAllParticipants = () => {
  if (selectedParticipantIds.value.length === participants.value.length) {
    selectedParticipantIds.value = []
  } else {
    selectedParticipantIds.value = participants.value.map(p => p.id!).filter(Boolean)
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

const runBalance = async () => {
  if (selectedParticipantIds.value.length < 10) {
    alert('최소 10명의 참가자가 필요합니다.')
    return
  }

  loading.value = true
  
  try {
    const selectedParticipants = participants.value.filter(p => selectedParticipantIds.value.includes(p.id!))
    const result = balanceTeams(selectedParticipants, { teamSize: 5 })
    balanceResult.value = result
  } catch (error) {
    alert('밸런싱 중 오류가 발생했습니다.')
  } finally {
    loading.value = false
  }
}

const getQualityClass = (score: number) => {
  if (score > 0.8) return 'quality-good'
  if (score > 0.6) return 'quality-medium'
  return 'quality-bad'
}

const getTierClass = (tier?: string) => {
  if (!tier) return 'tier-unranked'
  const tierUpper = tier.toUpperCase()
  
  switch (tierUpper) {
    case 'IRON': case 'I': return 'tier-iron'
    case 'BRONZE': case 'B': return 'tier-bronze'
    case 'SILVER': case 'S': return 'tier-silver'
    case 'GOLD': case 'G': return 'tier-gold'
    case 'PLATINUM': case 'P': return 'tier-platinum'
    case 'EMERALD': case 'E': return 'tier-emerald'
    case 'DIAMOND': case 'D': return 'tier-diamond'
    case 'MASTER': case 'M': return 'tier-master'
    case 'GRANDMASTER': case 'GM': return 'tier-grandmaster'
    case 'CHALLENGER': case 'C': return 'tier-challenger'
    default: return 'tier-unranked'
  }
}

const getLaneIcon = (lane?: string) => {
  if (!lane) return '❓'
  const laneUpper = lane.toUpperCase()
  
  switch (laneUpper) {
    case 'TOP': return '⚔️'
    case 'JUNGLE': return '🌿'
    case 'MID': return '⚡'
    case 'ADC': case 'BOT': return '🏹'
    case 'SUPPORT': return '🛡️'
    default: return '❓'
  }
}

const selectCaptain = (teamIndex: number, playerIndex: number) => {
  teamCaptains.value[teamIndex] = playerIndex
}

const isCaptain = (teamIndex: number, playerIndex: number): boolean => {
  return teamCaptains.value[teamIndex] === playerIndex
}

onMounted(() => {
  fetchMatches()
})
</script>

<style scoped>
.balance {
  max-width: 800px;
  margin: 0 auto;
}

.balance h2 {
  color: #333;
  margin-bottom: 1.5rem;
}

.form {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #333;
}

.match-list {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.match-btn {
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: all 0.3s;
}

.match-btn:hover {
  background: #f5f5f5;
}

.match-btn.active {
  background: #2196F3;
  color: white;
  border-color: #2196F3;
}

.player-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.select-all-btn {
  width: 100%;
  padding: 0.5rem;
  border: none;
  background: #f5f5f5;
  cursor: pointer;
  font-weight: bold;
  color: #2196F3;
}

.player-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  border-bottom: 1px solid #eee;
  cursor: pointer;
}

.player-item:hover {
  background: #f9f9f9;
}

.checkbox {
  margin-right: 0.75rem;
  font-size: 1.1rem;
}

.player-text {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.player-name {
  font-weight: 600;
  color: #333;
  min-width: 120px;
}

.tier-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
  color: white;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.lane-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.main-lane {
  font-weight: 500;
  color: #555;
}

.preferred-lanes {
  font-size: 0.75rem;
  color: #888;
  font-style: italic;
}

/* 티어별 색상 */
.tier-iron { background: #8B4513; }
.tier-bronze { background: #CD7F32; }
.tier-silver { background: #C0C0C0; color: #333; }
.tier-gold { background: #FFD700; color: #333; }
.tier-platinum { background: #00CED1; }
.tier-emerald { background: #50C878; }
.tier-diamond { background: #B9F2FF; color: #333; }
.tier-master { background: #8A2BE2; }
.tier-grandmaster { background: #FF4500; }
.tier-challenger { background: #FFD700; color: #333; }
.tier-unranked { background: #666; }

.button-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.balance-btn {
  flex: 1;
  background: #2196F3;
  color: white;
  border: none;
  padding: 0.75rem;
  border-radius: 4px;
  cursor: pointer;
}

.balance-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.balance-result {
  margin-top: 1.5rem;
}

.quality-score {
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quality-label {
  font-weight: bold;
}

.quality-value {
  font-size: 1.2rem;
  font-weight: bold;
}

.quality-good {
  color: #4CAF50;
}

.quality-medium {
  color: #FF9800;
}

.quality-bad {
  color: #F44336;
}

.team-card {
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  border: 1px solid #ddd;
}

.team-card h4 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.team-player {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  margin-bottom: 0.5rem;
  background: white;
  border-radius: 4px;
  border: 1px solid #eee;
  cursor: pointer;
  transition: all 0.2s ease;
}

.team-player:hover {
  background: #f5f5f5;
  border-color: #ddd;
}

.team-player.captain {
  background: #fff3cd;
  border-color: #ffc107;
  box-shadow: 0 2px 4px rgba(255, 193, 7, 0.2);
}

.captain-selector {
  min-width: 40px;
  text-align: center;
}

.captain-badge {
  font-size: 1.2rem;
  color: #ffc107;
}

.captain-select {
  font-size: 0.7rem;
  color: #666;
  padding: 0.2rem 0.4rem;
  background: #f8f9fa;
  border-radius: 3px;
  border: 1px solid #dee2e6;
}

.captain-select:hover {
  background: #e9ecef;
  color: #495057;
}

.team-player .player-name {
  min-width: 100px;
  font-weight: 600;
}

.team-player.captain .player-name {
  color: #856404;
}

.team-player .tier-badge {
  font-size: 0.7rem;
  padding: 0.2rem 0.4rem;
}

.team-player .lane-info {
  flex-direction: row;
  align-items: center;
  gap: 0.5rem;
}

.team-player .preferred-lanes {
  font-size: 0.7rem;
}
</style>
