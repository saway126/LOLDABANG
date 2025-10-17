<template>
  <div class="home">
    <h2>내전 종류</h2>
    
    <div class="type-cards">
      <div 
        v-for="matchType in matchTypes" 
        :key="matchType.key"
        class="type-card"
        @click="selectType(matchType.key)"
      >
        <div class="type-icon">{{ matchType.icon }}</div>
        <h3>{{ matchType.name }}</h3>
        <p>{{ matchType.desc }}</p>
        <div class="match-count">
          {{ getMatchCount(matchType.key) }}개의 내전
        </div>
      </div>
    </div>

    <!-- 선택된 종류의 내전 목록 -->
    <div v-if="selectedType" class="matches-section">
      <div class="section-header">
        <h3>{{ getSelectedTypeName() }} 내전 목록</h3>
        <button @click="selectedType = null" class="close-btn">✕</button>
      </div>
      
      <div v-if="loading" class="loading">
        내전 목록을 불러오는 중...
      </div>
      
      <div v-else-if="matches.length === 0" class="no-matches">
        아직 {{ getSelectedTypeName() }} 내전이 없습니다.
      </div>
      
      <div v-else class="matches-list">
        <div 
          v-for="match in matches" 
          :key="match.id"
          class="match-item"
        >
          <div class="match-info">
            <h4>{{ match.customId }}</h4>
            <p class="match-details">
              호스트: {{ match.host }} | 
              참가자: {{ match.participantCount }}명 | 
              {{ formatDate(match.createdAt) }}
            </p>
          </div>
          <div class="match-status" :class="match.status">
            {{ getStatusText(match.status) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface MatchType {
  key: string
  name: string
  desc: string
  icon: string
}

interface Match {
  id: number
  customId: string
  host: string
  type: string
  status: string
  createdAt: string
  participantCount: number
}

const selectedType = ref<string | null>(null)
const matches = ref<Match[]>([])
const loading = ref(false)
const matchCounts = ref<Record<string, number>>({})

const matchTypes: MatchType[] = [
  {
    key: 'soft',
    name: '소프트 피어리스',
    desc: '티어와 MMR을 중심으로 팀을 구성합니다.',
    icon: '🟢'
  },
  {
    key: 'hard',
    name: '하드 피어리스',
    desc: '주 라인을 최대한 보장하며 팀을 구성합니다.',
    icon: '🟡'
  },
  {
    key: 'hyper',
    name: '하이퍼 피어리스',
    desc: '모든 라인을 고려하여 최적의 조합을 찾습니다.',
    icon: '🔴'
  }
]

const API_BASE_URL = 'http://localhost:4000/api'

const selectType = async (type: string) => {
  selectedType.value = type
  loading.value = true
  
  try {
    const response = await fetch(`${API_BASE_URL}/matches/by-type/${type}`)
    const data = await response.json()
    matches.value = data
  } catch (error) {
    console.error('Failed to fetch matches:', error)
    matches.value = []
  } finally {
    loading.value = false
  }
}

const getSelectedTypeName = (): string => {
  const type = matchTypes.find(t => t.key === selectedType.value)
  return type ? type.name : ''
}

const getMatchCount = (type: string): number => {
  return matchCounts.value[type] || 0
}

const getStatusText = (status: string): string => {
  switch (status) {
    case 'open': return '모집중'
    case 'closed': return '마감'
    case 'in_progress': return '진행중'
    case 'completed': return '완료'
    default: return status
  }
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fetchMatchCounts = async () => {
  for (const type of matchTypes) {
    try {
      const response = await fetch(`${API_BASE_URL}/matches/by-type/${type.key}`)
      const data = await response.json()
      matchCounts.value[type.key] = data.length
    } catch (error) {
      console.error(`Failed to fetch count for ${type.key}:`, error)
      matchCounts.value[type.key] = 0
    }
  }
}

onMounted(() => {
  fetchMatchCounts()
})

// 페이지가 포커스될 때마다 내전 개수 새로고침
window.addEventListener('focus', () => {
  fetchMatchCounts()
})
</script>

<style scoped>
.home {
  max-width: 1000px;
  margin: 0 auto;
}

.home h2 {
  color: #333;
  margin-bottom: 1.5rem;
}

.type-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.type-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.type-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
  border-color: #007bff;
}

.type-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.type-card h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.type-card p {
  color: #666;
  margin: 0 0 1rem 0;
}

.match-count {
  background: #f8f9fa;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
}

.matches-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 1.5rem;
  margin-top: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.section-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 0.5rem;
  cursor: pointer;
  font-size: 1.2rem;
  color: #666;
}

.close-btn:hover {
  background: #e9ecef;
}

.loading, .no-matches {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.matches-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.match-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #007bff;
}

.match-info h4 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 1.1rem;
}

.match-details {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}

.match-status {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
}

.match-status.open {
  background: #d4edda;
  color: #155724;
}

.match-status.closed {
  background: #f8d7da;
  color: #721c24;
}

.match-status.in_progress {
  background: #fff3cd;
  color: #856404;
}

.match-status.completed {
  background: #d1ecf1;
  color: #0c5460;
}
</style>
