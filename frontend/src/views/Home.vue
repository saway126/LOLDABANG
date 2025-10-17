<template>
  <div class="home">
    <div class="welcome-section">
      <h2 class="welcome-title">🏠 롤다방에 오신 것을 환영합니다!</h2>
      <p class="welcome-subtitle">내전 종류를 선택하여 시작해보세요</p>
    </div>
    
    <div class="type-cards">
      <div 
        v-for="matchType in matchTypes" 
        :key="matchType.key"
        class="type-card"
        @click="selectType(matchType.key)"
      >
        <div class="card-image-container">
          <img 
            :src="getMatchTypeImage(matchType.key)" 
            :alt="matchType.name"
            class="card-background-image"
          />
          <div class="image-overlay"></div>
          <div class="card-header">
            <div class="type-icon">{{ matchType.icon }}</div>
            <div class="match-count-badge">
              {{ getMatchCount(matchType.key) }}개
            </div>
          </div>
        </div>
        <div class="card-content">
          <h3 class="type-name">{{ matchType.name }}</h3>
          <p class="type-desc">{{ matchType.desc }}</p>
          <div class="card-footer">
            <div class="click-hint">클릭하여 내전 목록 보기</div>
          </div>
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

// 환경에 따라 API URL 설정
const API_BASE_URL = import.meta.env.DEV 
  ? 'http://localhost:4000/api' 
  : 'https://backend-fvc5j1tr6-skwka12346-gmailcoms-projects.vercel.app/api'

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

const getMatchTypeImage = (type: string): string => {
  const imageMap: Record<string, string> = {
    'soft': '/images/soft-peerless.webp',
    'hard': '/images/hard-peerless.webp',
    'hyper': '/images/hyper-peerless.webp'
  }
  return imageMap[type] || '/images/soft-peerless.webp'
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.welcome-section {
  text-align: center;
  margin-bottom: 3rem;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(139, 69, 19, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(212, 196, 168, 0.3);
}

.welcome-title {
  color: #8B4513;
  margin: 0 0 0.5rem 0;
  font-size: 1.8rem;
  font-weight: bold;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
}

.welcome-subtitle {
  color: #A0522D;
  margin: 0;
  font-size: 1rem;
  opacity: 0.8;
}

.type-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.type-card {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(139, 69, 19, 0.15);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid rgba(212, 196, 168, 0.3);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  height: 400px;
}

.type-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  transition: left 0.5s;
}

.type-card:hover::before {
  left: 100%;
}

.type-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 16px 48px rgba(139, 69, 19, 0.25);
  border-color: #8B4513;
}

.type-card:hover .card-background-image {
  transform: scale(1.1);
}

.type-card:hover .image-overlay {
  opacity: 0.8;
}

.card-image-container {
  position: relative;
  height: 200px;
  overflow: hidden;
  border-radius: 20px 20px 0 0;
}

.card-background-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    135deg,
    rgba(139, 69, 19, 0.7) 0%,
    rgba(160, 82, 45, 0.5) 50%,
    rgba(139, 69, 19, 0.8) 100%
  );
  transition: opacity 0.3s ease;
}

.card-header {
  position: absolute;
  top: 1rem;
  left: 1rem;
  right: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 2;
}

.card-content {
  padding: 1.5rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.type-icon {
  font-size: 3rem;
  filter: drop-shadow(2px 2px 8px rgba(0, 0, 0, 0.5));
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
}

.match-count-badge {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(245, 241, 232, 0.9));
  color: #8B4513;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  border: 2px solid rgba(139, 69, 19, 0.3);
  backdrop-filter: blur(10px);
}

.type-name {
  margin: 0 0 1rem 0;
  color: #8B4513;
  font-size: 1.4rem;
  font-weight: bold;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
}

.type-desc {
  color: #A0522D;
  margin: 0 0 1.5rem 0;
  line-height: 1.6;
  font-size: 1rem;
}

.card-footer {
  border-top: 1px solid rgba(212, 196, 168, 0.5);
  padding-top: 1rem;
}

.click-hint {
  color: #8B4513;
  font-size: 0.85rem;
  opacity: 0.7;
  font-style: italic;
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

/* 반응형 디자인 */
@media (max-width: 768px) {
  .type-cards {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .type-card {
    height: 350px;
  }
  
  .card-image-container {
    height: 150px;
  }
  
  .type-icon {
    font-size: 2.5rem;
  }
  
  .match-count-badge {
    font-size: 0.8rem;
    padding: 0.4rem 0.8rem;
  }
  
  .type-name {
    font-size: 1.2rem;
  }
  
  .type-desc {
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .type-card {
    height: 320px;
  }
  
  .card-image-container {
    height: 120px;
  }
  
  .card-content {
    padding: 1rem;
  }
  
  .type-icon {
    font-size: 2rem;
  }
  
  .type-name {
    font-size: 1.1rem;
  }
  
  .type-desc {
    font-size: 0.85rem;
  }
}
</style>
