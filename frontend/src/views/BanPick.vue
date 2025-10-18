<template>
  <div class="banpick-container">
    <!-- 헤더 -->
    <div class="banpick-header">
      <h1>🎯 챔피언 밴픽 시스템</h1>
      <div class="header-info">
        <div class="match-info">
          <span class="match-id">{{ matchId }}</span>
          <span class="match-type">{{ getTypeText(matchType) }}</span>
        </div>
        <div class="phase-info">
          <span class="current-phase">{{ currentPhase }}</span>
          <span class="timer" v-if="timeLeft > 0">{{ timeLeft }}초</span>
        </div>
      </div>
    </div>

    <!-- 팀 정보 -->
    <div class="teams-section">
      <div class="team team-blue">
        <h3>🔵 블루팀</h3>
        <div class="team-players">
          <div v-for="(player, index) in blueTeam" :key="index" class="player-slot">
            <div class="player-info">
              <span class="player-name">{{ player.name }}</span>
              <span class="player-tier">{{ player.tier }} {{ player.rank }}</span>
            </div>
            <div class="champion-pick" v-if="player.champion">
              <img :src="player.champion.image" :alt="player.champion.name" class="champion-icon" />
              <span class="champion-name">{{ player.champion.name }}</span>
            </div>
            <div v-else class="pick-placeholder">선택 대기</div>
          </div>
        </div>
      </div>

      <div class="team team-red">
        <h3>🔴 레드팀</h3>
        <div class="team-players">
          <div v-for="(player, index) in redTeam" :key="index" class="player-slot">
            <div class="player-info">
              <span class="player-name">{{ player.name }}</span>
              <span class="player-tier">{{ player.tier }} {{ player.rank }}</span>
            </div>
            <div class="champion-pick" v-if="player.champion">
              <img :src="player.champion.image" :alt="player.champion.name" class="champion-icon" />
              <span class="champion-name">{{ player.champion.name }}</span>
            </div>
            <div v-else class="pick-placeholder">선택 대기</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 밴/픽 영역 -->
    <div class="banpick-area">
      <!-- 밴 영역 -->
      <div class="ban-section">
        <h3>🚫 밴</h3>
        <div class="ban-list">
          <div v-for="(ban, index) in bans" :key="index" class="ban-slot">
            <div v-if="ban" class="banned-champion">
              <img :src="ban.image" :alt="ban.name" class="champion-icon" />
              <span class="champion-name">{{ ban.name }}</span>
            </div>
            <div v-else class="ban-placeholder">
              <span class="ban-number">{{ index + 1 }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 픽 영역 -->
      <div class="pick-section">
        <h3>✅ 픽</h3>
        <div class="pick-list">
          <div v-for="(pick, index) in picks" :key="index" class="pick-slot">
            <div v-if="pick" class="picked-champion">
              <img :src="pick.image" :alt="pick.name" class="champion-icon" />
              <span class="champion-name">{{ pick.name }}</span>
              <span class="pick-team">{{ pick.team === 'blue' ? '🔵' : '🔴' }}</span>
            </div>
            <div v-else class="pick-placeholder">
              <span class="pick-number">{{ index + 1 }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 챔피언 선택 영역 -->
    <div class="champion-selection">
      <h3>챔피언 선택</h3>
      <div class="search-bar">
        <input 
          v-model="searchQuery" 
          @input="searchChampions" 
          placeholder="챔피언 검색..."
          class="search-input"
        />
      </div>
      
      <div class="champion-grid">
        <div 
          v-for="champion in filteredChampions" 
          :key="champion.id"
          class="champion-card"
          :class="{ 
            'banned': isBanned(champion.id),
            'picked': isPicked(champion.id),
            'disabled': isBanned(champion.id) || isPicked(champion.id)
          }"
          @click="selectChampion(champion)"
        >
          <img :src="champion.image" :alt="champion.name" class="champion-image" />
          <span class="champion-name">{{ champion.name }}</span>
          <div v-if="isBanned(champion.id)" class="status-badge banned">밴</div>
          <div v-if="isPicked(champion.id)" class="status-badge picked">픽</div>
        </div>
      </div>
    </div>

    <!-- 액션 버튼들 -->
    <div class="action-buttons">
      <button @click="startBanPick" :disabled="!canStart" class="action-btn start-btn">
        밴픽 시작
      </button>
      <button @click="resetBanPick" class="action-btn reset-btn">
        초기화
      </button>
      <button @click="saveBanPick" :disabled="!canSave" class="action-btn save-btn">
        저장
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

// 반응형 데이터
const matchId = ref(route.params.id || '내전001')
const matchType = ref('soft')
const currentPhase = ref('준비')
const timeLeft = ref(0)
const searchQuery = ref('')

// 팀 데이터
const blueTeam = ref([
  { name: '플레이어1', tier: 'Gold', rank: 'IV', champion: null },
  { name: '플레이어2', tier: 'Silver', rank: 'I', champion: null },
  { name: '플레이어3', tier: 'Gold', rank: 'II', champion: null },
  { name: '플레이어4', tier: 'Platinum', rank: 'III', champion: null },
  { name: '플레이어5', tier: 'Gold', rank: 'I', champion: null }
])

const redTeam = ref([
  { name: '플레이어6', tier: 'Gold', rank: 'III', champion: null },
  { name: '플레이어7', tier: 'Silver', rank: 'II', champion: null },
  { name: '플레이어8', tier: 'Gold', rank: 'IV', champion: null },
  { name: '플레이어9', tier: 'Platinum', rank: 'I', champion: null },
  { name: '플레이어10', tier: 'Gold', rank: 'II', champion: null }
])

// 밴/픽 데이터
const bans = ref(Array(10).fill(null))
const picks = ref(Array(10).fill(null))
const currentPickIndex = ref(0)
const currentBanIndex = ref(0)

// 챔피언 데이터 (실제로는 API에서 가져와야 함)
const champions = ref([
  { id: 1, name: '가렌', image: 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Garen.png' },
  { id: 2, name: '아리', image: 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Ahri.png' },
  { id: 3, name: '야스오', image: 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Yasuo.png' },
  { id: 4, name: '진', image: 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Jhin.png' },
  { id: 5, name: '럭스', image: 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Lux.png' },
  { id: 6, name: '다리우스', image: 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Darius.png' },
  { id: 7, name: '카타리나', image: 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Katarina.png' },
  { id: 8, name: '이즈리얼', image: 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Ezreal.png' },
  { id: 9, name: '소나', image: 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Sona.png' },
  { id: 10, name: '리신', image: 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/LeeSin.png' }
])

// 계산된 속성
const filteredChampions = computed(() => {
  if (!searchQuery.value) return champions.value
  return champions.value.filter(champion => 
    champion.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const canStart = computed(() => {
  return blueTeam.value.length === 5 && redTeam.value.length === 5
})

const canSave = computed(() => {
  return picks.value.some(pick => pick !== null)
})

// 메서드
const getTypeText = (type) => {
  const typeMap = {
    'soft': '소프트 피어리스',
    'hard': '하드 피어리스',
    'hyper': '하이퍼 피어리스'
  }
  return typeMap[type] || type
}

const searchChampions = () => {
  // 검색 로직은 computed 속성에서 처리
}

const isBanned = (championId) => {
  return bans.value.some(ban => ban && ban.id === championId)
}

const isPicked = (championId) => {
  return picks.value.some(pick => pick && pick.id === championId)
}

const selectChampion = (champion) => {
  if (isBanned(champion.id) || isPicked(champion.id)) {
    return
  }

  // 현재 밴/픽 단계에 따라 처리
  if (currentPhase.value === '밴 단계') {
    if (currentBanIndex.value < bans.value.length) {
      bans.value[currentBanIndex.value] = champion
      currentBanIndex.value++
      
      if (currentBanIndex.value >= bans.value.length) {
        currentPhase.value = '픽 단계'
      }
    }
  } else if (currentPhase.value === '픽 단계') {
    if (currentPickIndex.value < picks.value.length) {
      const team = currentPickIndex.value % 2 === 0 ? 'blue' : 'red'
      picks.value[currentPickIndex.value] = { ...champion, team }
      currentPickIndex.value++
      
      if (currentPickIndex.value >= picks.value.length) {
        currentPhase.value = '완료'
      }
    }
  }
}

const startBanPick = () => {
  currentPhase.value = '밴 단계'
  currentBanIndex.value = 0
  currentPickIndex.value = 0
  timeLeft.value = 30 // 30초 타이머
}

const resetBanPick = () => {
  bans.value = Array(10).fill(null)
  picks.value = Array(10).fill(null)
  currentBanIndex.value = 0
  currentPickIndex.value = 0
  currentPhase.value = '준비'
  timeLeft.value = 0
}

const saveBanPick = () => {
  // 밴픽 결과 저장 로직
  console.log('밴픽 결과 저장:', { bans: bans.value, picks: picks.value })
  alert('밴픽 결과가 저장되었습니다!')
}

// 라이프사이클
onMounted(() => {
  // 초기 데이터 로드
})
</script>

<style scoped>
.banpick-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  min-height: 100vh;
  color: white;
}

.banpick-header {
  text-align: center;
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-radius: 15px;
  backdrop-filter: blur(10px);
}

.banpick-header h1 {
  margin: 0 0 15px 0;
  font-size: 2.5rem;
  font-weight: bold;
}

.header-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.match-info, .phase-info {
  display: flex;
  gap: 15px;
  align-items: center;
}

.match-id, .current-phase {
  font-size: 1.2rem;
  font-weight: bold;
}

.match-type {
  background: rgba(255, 255, 255, 0.2);
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 0.9rem;
}

.timer {
  background: #ff6b6b;
  padding: 5px 15px;
  border-radius: 20px;
  font-weight: bold;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.teams-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.team {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 20px;
  backdrop-filter: blur(10px);
}

.team h3 {
  margin: 0 0 15px 0;
  font-size: 1.3rem;
  text-align: center;
}

.team-players {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.player-slot {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.player-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.player-name {
  font-weight: bold;
  font-size: 1rem;
}

.player-tier {
  font-size: 0.8rem;
  opacity: 0.8;
}

.champion-pick {
  display: flex;
  align-items: center;
  gap: 10px;
}

.champion-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.champion-name {
  font-size: 0.9rem;
  font-weight: bold;
}

.pick-placeholder {
  color: rgba(255, 255, 255, 0.6);
  font-style: italic;
}

.banpick-area {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.ban-section, .pick-section {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 20px;
  backdrop-filter: blur(10px);
}

.ban-section h3, .pick-section h3 {
  margin: 0 0 15px 0;
  font-size: 1.2rem;
  text-align: center;
}

.ban-list, .pick-list {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
}

.ban-slot, .pick-slot {
  aspect-ratio: 1;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.banned-champion, .picked-champion {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.banned-champion .champion-icon {
  width: 30px;
  height: 30px;
  filter: grayscale(100%);
  opacity: 0.6;
}

.picked-champion .champion-icon {
  width: 30px;
  height: 30px;
}

.pick-team {
  font-size: 0.8rem;
}

.ban-placeholder, .pick-placeholder {
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.8rem;
}

.ban-number, .pick-number {
  font-weight: bold;
  font-size: 1.2rem;
}

.champion-selection {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 20px;
  margin-bottom: 30px;
  backdrop-filter: blur(10px);
}

.champion-selection h3 {
  margin: 0 0 20px 0;
  font-size: 1.3rem;
  text-align: center;
}

.search-bar {
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
  padding: 12px 20px;
  border: none;
  border-radius: 25px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 1rem;
  backdrop-filter: blur(10px);
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.champion-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 10px;
  max-height: 300px;
  overflow-y: auto;
}

.champion-card {
  aspect-ratio: 1;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.champion-card:hover:not(.disabled) {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

.champion-card.disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.champion-card.banned {
  background: rgba(255, 0, 0, 0.3);
}

.champion-card.picked {
  background: rgba(0, 255, 0, 0.3);
}

.champion-image {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.champion-name {
  font-size: 0.7rem;
  text-align: center;
  margin-top: 5px;
  font-weight: bold;
}

.status-badge {
  position: absolute;
  top: 5px;
  right: 5px;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 0.6rem;
  font-weight: bold;
}

.status-badge.banned {
  background: #ff6b6b;
  color: white;
}

.status-badge.picked {
  background: #51cf66;
  color: white;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.action-btn {
  padding: 12px 30px;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.start-btn {
  background: #51cf66;
  color: white;
}

.start-btn:hover:not(:disabled) {
  background: #40c057;
  transform: translateY(-2px);
}

.reset-btn {
  background: #ffd43b;
  color: #333;
}

.reset-btn:hover {
  background: #fab005;
  transform: translateY(-2px);
}

.save-btn {
  background: #339af0;
  color: white;
}

.save-btn:hover:not(:disabled) {
  background: #228be6;
  transform: translateY(-2px);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .teams-section {
    grid-template-columns: 1fr;
  }
  
  .banpick-area {
    grid-template-columns: 1fr;
  }
  
  .ban-list, .pick-list {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .champion-grid {
    grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
}
</style>
