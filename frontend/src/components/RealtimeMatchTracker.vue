<template>
  <div class="realtime-tracker">
    <!-- 실시간 알림 표시 -->
    <div v-if="notifications.length > 0" class="notifications-container">
      <div 
        v-for="notification in notifications" 
        :key="notification.id"
        class="notification"
        :class="notification.type"
        @click="removeNotification(notification.id)"
      >
        <div class="notification-icon">
          {{ getNotificationIcon(notification.type) }}
        </div>
        <div class="notification-content">
          <div class="notification-title">{{ notification.title }}</div>
          <div class="notification-message">{{ notification.message }}</div>
          <div class="notification-time">{{ formatTime(notification.timestamp) }}</div>
        </div>
        <button class="notification-close" @click.stop="removeNotification(notification.id)">
          ×
        </button>
      </div>
    </div>

    <!-- 실시간 내전 상태 표시 -->
    <div class="match-status-display">
      <div class="status-header">
        <h3>🔥 실시간 내전 현황</h3>
        <div class="connection-indicator" :class="wsConnected ? 'connected' : 'disconnected'">
          {{ wsConnected ? '🟢 실시간 연결됨' : '🔴 연결 끊김' }}
        </div>
      </div>
      
      <div class="matches-overview">
        <div class="status-card">
          <div class="status-icon">⚡</div>
          <div class="status-info">
            <div class="status-count">{{ activeMatches.length }}</div>
            <div class="status-label">진행 중</div>
          </div>
        </div>
        
        <div class="status-card">
          <div class="status-icon">✅</div>
          <div class="status-info">
            <div class="status-count">{{ completedToday }}</div>
            <div class="status-label">오늘 완료</div>
          </div>
        </div>
        
        <div class="status-card">
          <div class="status-icon">👥</div>
          <div class="status-info">
            <div class="status-count">{{ totalParticipants }}</div>
            <div class="status-label">총 참가자</div>
          </div>
        </div>
      </div>

      <!-- 실시간 내전 목록 -->
      <div class="realtime-matches">
        <div v-if="activeMatches.length === 0" class="no-matches">
          <div class="no-matches-icon">😴</div>
          <p>현재 진행 중인 내전이 없습니다</p>
        </div>
        
        <div v-else class="matches-list">
          <div 
            v-for="match in activeMatches" 
            :key="match.id"
            class="match-card"
            :class="getMatchStatusClass(match.status)"
          >
            <div class="match-header">
              <div class="match-id">{{ match.customId }}</div>
              <div class="match-status" :class="match.status">
                {{ getStatusText(match.status) }}
              </div>
            </div>
            
            <div class="match-info">
              <div class="match-host">진행자: {{ match.host }}</div>
              <div class="match-type">종류: {{ getTypeText(match.type) }}</div>
              <div class="match-participants">참가자: {{ match.participantCount }}명</div>
              <div class="match-duration">
                진행시간: {{ getMatchDuration(match.startedAt) }}
              </div>
            </div>

            <div class="match-actions">
              <button @click="viewMatch(match.id)" class="action-btn view">
                👁️ 상세보기
              </button>
              <button 
                v-if="match.status === 'open'" 
                @click="startMatch(match.id)" 
                class="action-btn start"
              >
                ▶️ 시작
              </button>
              <button 
                v-if="match.status === 'in_progress'" 
                @click="endMatch(match.id)" 
                class="action-btn end"
              >
                🏁 종료
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useWebSocket } from '../composables/useWebSocket'

// API 설정
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://loldabang-production.up.railway.app/api'
const WS_URL = import.meta.env.VITE_WS_URL || 'wss://loldabang-production.up.railway.app/ws'

// 반응형 데이터
const activeMatches = ref([])
const notifications = ref([])
const completedToday = ref(0)
const lastUpdateTime = ref('')

// WebSocket 연결
const { isConnected: wsConnected, send: wsSend } = useWebSocket(WS_URL, {
  onMessage: handleWebSocketMessage,
  onOpen: () => {
    console.log('✅ 실시간 내전 추적기 WebSocket 연결됨')
  },
  onClose: () => {
    console.log('❌ 실시간 내전 추적기 WebSocket 연결 끊김')
  },
  onError: (error) => {
    console.error('❌ 실시간 내전 추적기 WebSocket 오류:', error)
  }
})

// 계산된 속성
const totalParticipants = computed(() => {
  return activeMatches.value.reduce((sum, match) => sum + match.participantCount, 0)
})

// 메서드
const fetchActiveMatches = async () => {
  try {
    console.log('📡 활성 내전 데이터 로드 중...')
    const allTypes = ['soft', 'hard', 'hyper']
    let allMatches = []
    
    for (const type of allTypes) {
      try {
        const typeResponse = await fetch(`${API_BASE_URL}/matches/by-type/${type}`)
        if (typeResponse.ok) {
          const typeMatches = await typeResponse.json()
          allMatches = allMatches.concat(typeMatches)
        }
      } catch (typeError) {
        console.warn(`❌ ${type} 타입 내전 로드 실패:`, typeError)
      }
    }
    
    // 활성 내전 필터링 (open과 in_progress 상태)
    const filteredMatches = allMatches.filter(match => {
      const isActive = match.status === 'open' || match.status === 'in_progress'
      console.log(`🔍 내전 ${match.customId}: 상태=${match.status}, 활성=${isActive}`)
      return isActive
    })
    
    // 상태 변경 감지
    const previousMatches = activeMatches.value
    const newMatches = filteredMatches.filter(newMatch => 
      !previousMatches.some(prevMatch => prevMatch.id === newMatch.id)
    )
    const endedMatches = previousMatches.filter(prevMatch => 
      !filteredMatches.some(newMatch => newMatch.id === prevMatch.id)
    )
    
    // 새로 시작된 내전 알림
    newMatches.forEach(match => {
      addNotification('success', '새 내전 시작', `${match.customId} 내전이 시작되었습니다!`)
    })
    
    // 종료된 내전 알림
    endedMatches.forEach(match => {
      addNotification('info', '내전 종료', `${match.customId} 내전이 종료되었습니다.`)
    })
    
    activeMatches.value = filteredMatches
    lastUpdateTime.value = new Date().toLocaleTimeString('ko-KR')
    
    console.log(`🎯 총 ${allMatches.length}개 내전 중 ${filteredMatches.length}개 활성 내전 표시`)
    
  } catch (error) {
    console.error('❌ 활성 내전 데이터 로드 실패:', error)
  }
}

const handleWebSocketMessage = (data) => {
  console.log('📨 WebSocket 메시지 수신:', data)
  
  switch (data.type) {
    case 'match_status_update':
      fetchActiveMatches()
      break
    case 'match_started':
      addNotification('success', '내전 시작', `${data.matchId} 내전이 시작되었습니다!`)
      fetchActiveMatches()
      break
    case 'match_ended':
      addNotification('info', '내전 종료', `${data.matchId} 내전이 종료되었습니다.`)
      fetchActiveMatches()
      break
    case 'admin_notification':
      addNotification('warning', '관리자 알림', data.message)
      break
  }
}

const addNotification = (type, title, message) => {
  const notification = {
    id: Date.now() + Math.random(),
    type,
    title,
    message,
    timestamp: new Date()
  }
  
  notifications.value.unshift(notification)
  
  // 5초 후 자동 제거
  setTimeout(() => {
    removeNotification(notification.id)
  }, 5000)
}

const removeNotification = (id) => {
  const index = notifications.value.findIndex(n => n.id === id)
  if (index > -1) {
    notifications.value.splice(index, 1)
  }
}

const getNotificationIcon = (type) => {
  const icons = {
    success: '✅',
    info: 'ℹ️',
    warning: '⚠️',
    error: '❌'
  }
  return icons[type] || '📢'
}

const getMatchStatusClass = (status) => {
  return {
    'status-open': status === 'open',
    'status-in-progress': status === 'in_progress',
    'status-completed': status === 'completed',
    'status-closed': status === 'closed'
  }
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
    'soft': '소프트 피어리스',
    'hard': '하드 피어리스',
    'hyper': '하이퍼 피어리스'
  }
  return typeMap[type] || type
}

const getMatchDuration = (startedAt) => {
  if (!startedAt) return '알 수 없음'
  
  const start = new Date(startedAt)
  const now = new Date()
  const diff = now - start
  
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  
  if (hours > 0) {
    return `${hours}시간 ${minutes}분`
  } else {
    return `${minutes}분`
  }
}

const formatTime = (timestamp) => {
  return timestamp.toLocaleTimeString('ko-KR')
}

const viewMatch = (matchId) => {
  // 내전 상세 페이지로 이동
  window.location.href = `/match/${matchId}`
}

const startMatch = async (matchId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/matches/${matchId}/status`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status: 'in_progress' })
    })

    if (response.ok) {
      addNotification('success', '내전 시작', '내전이 시작되었습니다!')
      fetchActiveMatches()
    } else {
      throw new Error('내전 시작 실패')
    }
  } catch (error) {
    console.error('내전 시작 실패:', error)
    addNotification('error', '오류', '내전 시작에 실패했습니다.')
  }
}

const endMatch = async (matchId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/matches/${matchId}/status`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status: 'completed' })
    })

    if (response.ok) {
      addNotification('info', '내전 종료', '내전이 종료되었습니다.')
      fetchActiveMatches()
    } else {
      throw new Error('내전 종료 실패')
    }
  } catch (error) {
    console.error('내전 종료 실패:', error)
    addNotification('error', '오류', '내전 종료에 실패했습니다.')
  }
}

// 라이프사이클
onMounted(() => {
  fetchActiveMatches()
  
  // 30초마다 데이터 새로고침
  const interval = setInterval(fetchActiveMatches, 30000)
  
  onUnmounted(() => {
    clearInterval(interval)
  })
})
</script>

<style scoped>
.realtime-tracker {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.notifications-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  max-width: 400px;
}

.notification {
  display: flex;
  align-items: flex-start;
  background: white;
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid #ddd;
}

.notification:hover {
  transform: translateX(-5px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.notification.success {
  border-left-color: #4CAF50;
}

.notification.info {
  border-left-color: #2196F3;
}

.notification.warning {
  border-left-color: #FF9800;
}

.notification.error {
  border-left-color: #f44336;
}

.notification-icon {
  font-size: 1.5rem;
  margin-right: 10px;
  margin-top: 2px;
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.notification-message {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.notification-time {
  color: #999;
  font-size: 0.8rem;
}

.notification-close {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.match-status-display {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.status-header h3 {
  color: #333;
  margin: 0;
  font-size: 1.5rem;
  font-weight: bold;
}

.connection-indicator {
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: bold;
  font-size: 0.9rem;
}

.connection-indicator.connected {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
}

.connection-indicator.disconnected {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
}

.matches-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.status-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 15px;
  text-align: center;
  transition: transform 0.3s ease;
}

.status-card:hover {
  transform: translateY(-5px);
}

.status-icon {
  font-size: 2rem;
  margin-bottom: 10px;
}

.status-count {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 5px;
}

.status-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

.realtime-matches h4 {
  color: #333;
  margin-bottom: 20px;
  font-size: 1.2rem;
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

.matches-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.match-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border-left: 4px solid #ddd;
}

.match-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.match-card.status-open {
  border-left-color: #4CAF50;
}

.match-card.status-in-progress {
  border-left-color: #FF9800;
}

.match-card.status-completed {
  border-left-color: #2196F3;
}

.match-card.status-closed {
  border-left-color: #f44336;
}

.match-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.match-id {
  font-weight: bold;
  font-size: 1.1rem;
  color: #333;
}

.match-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
  text-transform: uppercase;
}

.match-status.open {
  background: #e8f5e8;
  color: #4CAF50;
}

.match-status.in_progress {
  background: #fff3e0;
  color: #FF9800;
}

.match-status.completed {
  background: #e3f2fd;
  color: #2196F3;
}

.match-status.closed {
  background: #ffebee;
  color: #f44336;
}

.match-info {
  margin-bottom: 20px;
}

.match-info > div {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  padding: 5px 0;
}

.match-info .label {
  color: #666;
  font-weight: 500;
}

.match-info .value {
  color: #333;
  font-weight: bold;
}

.match-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: bold;
  transition: all 0.3s ease;
  flex: 1;
  min-width: 80px;
}

.action-btn.view {
  background: #e3f2fd;
  color: #2196F3;
}

.action-btn.start {
  background: #e8f5e8;
  color: #4CAF50;
}

.action-btn.end {
  background: #ffebee;
  color: #f44336;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

@media (max-width: 768px) {
  .notifications-container {
    position: fixed;
    top: 10px;
    right: 10px;
    left: 10px;
    max-width: none;
  }
  
  .matches-list {
    grid-template-columns: 1fr;
  }
  
  .match-actions {
    flex-direction: column;
  }
  
  .action-btn {
    flex: none;
  }
}
</style>
