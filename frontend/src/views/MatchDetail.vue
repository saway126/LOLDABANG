<template>
  <div class="match-detail">
    <div class="page-header">
      <button @click="goBack" class="back-btn">← 뒤로가기</button>
      <h2 class="page-title">📋 내전 상세 정보</h2>
    </div>
    
    <div v-if="loading" class="loading">
      내전 정보를 불러오는 중...
    </div>
    
    <div v-else-if="match" class="match-container">
      <!-- 내전 기본 정보 -->
      <div class="match-info-section">
        <h3 class="section-title">📝 내전 정보</h3>
        <div class="info-grid">
          <div class="info-item">
            <label>내전 ID</label>
            <span class="info-value">{{ match.customId }}</span>
          </div>
          <div class="info-item">
            <label>진행자</label>
            <span class="info-value">{{ match.host }}</span>
          </div>
          <div class="info-item">
            <label>내전 종류</label>
            <span class="info-value type-badge" :class="match.type">
              {{ getTypeName(match.type) }}
            </span>
          </div>
          <div class="info-item">
            <label>상태</label>
            <span class="info-value status-badge" :class="match.status">
              {{ getStatusText(match.status) }}
            </span>
          </div>
          <div class="info-item">
            <label>생성일</label>
            <span class="info-value">{{ formatDate(match.createdAt) }}</span>
          </div>
          <div class="info-item">
            <label>참가자 수</label>
            <span class="info-value">{{ match.participantCount }}명</span>
          </div>
        </div>
      </div>
      
      <!-- 참가자 목록 -->
      <div class="participants-section">
        <h3 class="section-title">👥 참가자 목록</h3>
        <div v-if="participants.length === 0" class="no-participants">
          참가자가 없습니다.
        </div>
        <div v-else class="participants-grid">
          <div 
            v-for="participant in participants" 
            :key="participant.id"
            class="participant-card"
          >
            <div class="participant-info">
              <div class="participant-name">{{ participant.name }}</div>
              <div class="participant-details">
                <span class="tier">{{ participant.tier }}{{ participant.rank }}</span>
                <span class="lane">{{ participant.mainLane }}</span>
              </div>
              <div v-if="participant.preferredLanes && participant.preferredLanes.length > 0" class="preferred-lanes">
                희망라인: {{ participant.preferredLanes.join(', ') }}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 액션 버튼들 -->
      <div class="action-buttons">
        <button @click="editMatch" class="action-btn edit-btn">
          ✏️ 수정하기
        </button>
        <button @click="deleteMatch" class="action-btn delete-btn">
          🗑️ 삭제하기
        </button>
      </div>
    </div>
    
    <div v-else class="error">
      <div class="error-content">
        <h3>❌ 내전을 찾을 수 없습니다</h3>
        <p>요청하신 내전이 존재하지 않거나 삭제되었습니다.</p>
        <div class="error-actions">
          <button @click="goBack" class="action-btn back-btn">← 뒤로가기</button>
          <button @click="goHome" class="action-btn home-btn">🏠 홈으로</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const match = ref<any>(null)
const participants = ref<any[]>([])

// 환경에 따라 API URL 설정
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (import.meta.env.DEV 
    ? 'http://localhost:4000/api' 
    : 'https://loldabang-production.up.railway.app/api')

// 내전 상세 정보 로드
const loadMatchDetail = async () => {
  const matchId = route.params.id
  if (!matchId) return
  
  loading.value = true
  
  try {
    // 내전 기본 정보 로드
    const matchResponse = await fetch(`${API_BASE_URL}/matches/${matchId}`)
    if (matchResponse.ok) {
      match.value = await matchResponse.json()
    } else {
      throw new Error('내전 정보를 불러올 수 없습니다.')
    }
    
    // 참가자 정보 로드
    const participantsResponse = await fetch(`${API_BASE_URL}/matches/${matchId}/participants`)
    if (participantsResponse.ok) {
      participants.value = await participantsResponse.json()
    }
    
  } catch (error) {
    console.error('내전 상세 정보 로드 실패:', error)
    alert('내전 정보를 불러오는데 실패했습니다.')
  } finally {
    loading.value = false
  }
}

// 뒤로가기
const goBack = () => {
  router.back()
}

// 홈으로 이동
const goHome = () => {
  router.push('/')
}

// 내전 수정
const editMatch = () => {
  router.push(`/create?edit=${match.value.id}`)
}

// 내전 삭제
const deleteMatch = async () => {
  if (!confirm(`정말로 "${match.value.customId}" 내전을 삭제하시겠습니까?`)) {
    return
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}/matches/${match.value.id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      }
    })
    
    if (response.ok) {
      alert('내전이 삭제되었습니다.')
      router.push('/')
    } else {
      throw new Error('삭제 실패')
    }
  } catch (error) {
    console.error('내전 삭제 실패:', error)
    alert('내전 삭제에 실패했습니다.')
  }
}

// 유틸리티 함수들
const getTypeName = (type: string) => {
  const typeNames: Record<string, string> = {
    'soft': '소프트 피어리스',
    'hard': '하드 피어리스',
    'hyper': '하이퍼 피어리스'
  }
  return typeNames[type] || type
}

const getStatusText = (status: string) => {
  const statusTexts: Record<string, string> = {
    'open': '모집중',
    'closed': '마감',
    'in_progress': '진행중',
    'completed': '완료'
  }
  return statusTexts[status] || status
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadMatchDetail()
})
</script>

<style scoped>
.match-detail {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 1rem;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.back-btn {
  padding: 0.5rem 1rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s ease;
}

.back-btn:hover {
  background: #5a6268;
}

.page-title {
  color: #8B4513;
  margin: 0;
  font-size: 2rem;
  font-weight: bold;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
}

.loading, .error {
  text-align: center;
  padding: 3rem;
  font-size: 1.1rem;
  color: #6c757d;
}

.match-container {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(139, 69, 19, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(212, 196, 168, 0.3);
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

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-item label {
  font-weight: bold;
  color: #8B4513;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 1rem;
  color: #333;
}

.type-badge, .status-badge {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  text-align: center;
}

.type-badge.soft {
  background: #d4edda;
  color: #155724;
}

.type-badge.hard {
  background: #f8d7da;
  color: #721c24;
}

.type-badge.hyper {
  background: #fff3cd;
  color: #856404;
}

.status-badge.open {
  background: #d4edda;
  color: #155724;
}

.status-badge.closed {
  background: #f8d7da;
  color: #721c24;
}

.status-badge.in_progress {
  background: #fff3cd;
  color: #856404;
}

.status-badge.completed {
  background: #d1ecf1;
  color: #0c5460;
}

.participants-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.participant-card {
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid #d4c4a8;
  border-radius: 12px;
  padding: 1rem;
  transition: all 0.2s ease;
}

.participant-card:hover {
  border-color: #8B4513;
  box-shadow: 0 4px 12px rgba(139, 69, 19, 0.1);
}

.participant-name {
  font-weight: bold;
  color: #8B4513;
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
}

.participant-details {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.tier {
  background: #e9ecef;
  color: #495057;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.lane {
  background: #d4edda;
  color: #155724;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.preferred-lanes {
  font-size: 0.8rem;
  color: #6c757d;
  font-style: italic;
}

.no-participants {
  text-align: center;
  color: #6c757d;
  font-style: italic;
  padding: 2rem;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #d4c4a8;
}

.action-btn {
  padding: 0.8rem 2rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.edit-btn {
  background: #28a745;
  color: white;
}

.edit-btn:hover {
  background: #1e7e34;
}

.delete-btn {
  background: #dc3545;
  color: white;
}

.delete-btn:hover {
  background: #c82333;
}

.error {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.error-content {
  text-align: center;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  padding: 3rem;
  box-shadow: 0 8px 32px rgba(139, 69, 19, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(212, 196, 168, 0.3);
}

.error-content h3 {
  color: #dc3545;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.error-content p {
  color: #6c757d;
  margin-bottom: 2rem;
  font-size: 1.1rem;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.back-btn {
  background: #6c757d;
  color: white;
}

.back-btn:hover {
  background: #5a6268;
}

.home-btn {
  background: #007bff;
  color: white;
}

.home-btn:hover {
  background: #0056b3;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .participants-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
