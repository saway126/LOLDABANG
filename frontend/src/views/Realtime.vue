<template>
  <div class="realtime-container">
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

    <!-- 헤더 -->
    <div class="realtime-header">
      <h1>🎮 실시간 내전 관리</h1>
      <div class="header-controls">
        <button @click="refreshData" :disabled="loading" class="refresh-btn">
          <span v-if="loading">🔄</span>
          <span v-else>새로고침</span>
        </button>
        <div class="last-updated">
          마지막 업데이트: {{ lastUpdated }}
        </div>
      </div>
    </div>

    <!-- 실시간 내전 목록 -->
    <div class="matches-section">
      <h2>🔥 활성 내전 ({{ realtimeMatches.length }}개)</h2>
      
      <!-- 실시간 상태 표시 -->
      <div class="realtime-status">
        <div class="status-indicator" :class="wsConnected ? 'connected' : 'polling'">
          {{ wsConnected ? '🟢 실시간 연결됨' : '🔄 폴링 모드 (5초마다 업데이트)' }}
        </div>
        <div class="last-updated">
          마지막 업데이트: {{ lastUpdated }}
        </div>
      </div>
      
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>실시간 데이터 로딩 중...</p>
      </div>

      <div v-else-if="realtimeMatches.length === 0" class="no-matches">
        <div class="no-matches-icon">😴</div>
        <h3>현재 활성 내전이 없습니다</h3>
        <p>새로운 내전이 생성되면 여기에 표시됩니다.</p>
      </div>

      <div v-else class="matches-grid">
        <div 
          v-for="match in realtimeMatches" 
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
            <div class="match-host">
              <span class="label">진행자:</span>
              <span class="value">{{ match.host }}</span>
            </div>
            <div class="match-type">
              <span class="label">종류:</span>
              <span class="value type-badge" :class="match.type">
                {{ getTypeText(match.type) }}
              </span>
            </div>
            <div class="match-participants">
              <span class="label">참가자:</span>
              <span class="value">{{ match.participantCount }}명</span>
            </div>
            <div class="match-time">
              <span class="label">생성시간:</span>
              <span class="value">{{ formatTime(match.createdAt) }}</span>
            </div>
          </div>

          <div class="match-actions">
            <button @click="viewMatch(match.id)" class="action-btn view">
              👁️ 상세보기
            </button>
            <button @click="updateMatchStatus(match.customId, 'in_progress')" 
                    v-if="match.status === 'open'" 
                    class="action-btn start">
              ▶️ 시작
            </button>
            <button @click="updateMatchStatus(match.customId, 'completed')" 
                    v-if="match.status === 'in_progress'" 
                    class="action-btn complete">
              ✅ 완료
            </button>
            <button @click="updateMatchStatus(match.customId, 'closed')" 
                    v-if="match.status === 'open'" 
                    class="action-btn close">
              ❌ 종료
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 통계 섹션 -->
    <div class="stats-section">
      <h2>📊 실시간 통계</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">🔥</div>
          <div class="stat-content">
            <div class="stat-value">{{ realtimeMatches.length }}</div>
            <div class="stat-label">활성 내전</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-content">
            <div class="stat-value">{{ totalParticipants }}</div>
            <div class="stat-label">총 참가자</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⚡</div>
          <div class="stat-content">
            <div class="stat-value">{{ inProgressMatches }}</div>
            <div class="stat-label">진행 중</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">✅</div>
          <div class="stat-content">
            <div class="stat-value">{{ completedToday }}</div>
            <div class="stat-label">오늘 완료</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// API 설정
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://loldabang-production.up.railway.app/api'

// 반응형 데이터
const realtimeMatches = ref([])
const loading = ref(false)
const lastUpdated = ref('')
const refreshInterval = ref(null)
const wsConnected = ref(false)
const ws = ref(null)
const notifications = ref([])

// 계산된 속성
const totalParticipants = computed(() => {
  return realtimeMatches.value.reduce((sum, match) => sum + match.participantCount, 0)
})

const inProgressMatches = computed(() => {
  return realtimeMatches.value.filter(match => match.status === 'in_progress').length
})

const completedToday = computed(() => {
  // 실제로는 백엔드에서 오늘 완료된 내전 수를 가져와야 함
  return 0
})

// WebSocket 연결 (폴링 방식으로 대체)
const connectWebSocket = () => {
  try {
    const WS_URL = import.meta.env.VITE_WS_URL || 'wss://loldabang-production.up.railway.app/ws'
    console.log('🔌 WebSocket 연결 시도:', WS_URL)
    
    ws.value = new WebSocket(WS_URL)
    
    ws.value.onopen = () => {
      wsConnected.value = true
      console.log('✅ WebSocket 연결됨')
      // 연결 성공 시 ping 전송
      ws.value.send(JSON.stringify({ type: 'ping' }))
    }
    
    ws.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('📨 WebSocket 메시지 수신:', data)
        handleWebSocketMessage(data)
      } catch (error) {
        console.error('❌ WebSocket 메시지 파싱 오류:', error)
      }
    }
    
    ws.value.onclose = (event) => {
      wsConnected.value = false
      console.log('❌ WebSocket 연결 끊김:', event.code, event.reason)
      // WebSocket 연결 실패 시 폴링 방식으로 전환
      console.log('🔄 폴링 방식으로 전환...')
      startPolling()
    }
    
    ws.value.onerror = (error) => {
      console.error('❌ WebSocket 오류:', error)
      wsConnected.value = false
      // WebSocket 오류 시 폴링 방식으로 전환
      console.log('🔄 폴링 방식으로 전환...')
      startPolling()
    }
  } catch (error) {
    console.error('❌ WebSocket 연결 실패:', error)
    wsConnected.value = false
    // WebSocket 연결 실패 시 폴링 방식으로 전환
    console.log('🔄 폴링 방식으로 전환...')
    startPolling()
  }
}

// 폴링 방식으로 실시간 업데이트
const startPolling = () => {
  console.log('📡 폴링 방식으로 실시간 업데이트 시작')
  wsConnected.value = false // 폴링 모드 표시
  
  // 30초마다 데이터 새로고침 (빈도 조정)
  const pollingInterval = setInterval(() => {
    console.log('🔄 폴링으로 데이터 새로고침...')
    fetchRealtimeMatches()
  }, 30000)
  
  // 컴포넌트 언마운트 시 폴링 중지
  onUnmounted(() => {
    clearInterval(pollingInterval)
  })
}

const handleWebSocketMessage = (data) => {
  console.log('📨 WebSocket 메시지 처리:', data.type)
  
  switch (data.type) {
    case 'pong':
      console.log('🏓 WebSocket pong 수신')
      break
    case 'match_status_update':
      console.log('🔄 내전 상태 업데이트 수신')
      fetchRealtimeMatches()
      break
    case 'match_started':
      console.log('▶️ 내전 시작 알림:', data.matchId)
      addNotification('success', '내전 시작', `내전 ${data.matchId}이 시작되었습니다!`)
      fetchRealtimeMatches()
      break
    case 'match_ended':
      console.log('🏁 내전 종료 알림:', data.matchId)
      addNotification('info', '내전 종료', `내전 ${data.matchId}이 종료되었습니다.`)
      fetchRealtimeMatches()
      break
    case 'admin_notification':
      console.log('📢 관리자 알림 수신')
      addNotification('warning', '관리자 알림', data.message)
      break
    default:
      console.log('❓ 알 수 없는 메시지 타입:', data.type)
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
  
  // 브라우저 알림
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(title, {
      body: message,
      icon: '/favicon.ico'
    })
  }
}

const removeNotification = (id) => {
  const index = notifications.value.findIndex(n => n.id === id)
  if (index > -1) {
    notifications.value.splice(index, 1)
  }
}

// 메서드
const fetchRealtimeMatches = async () => {
  try {
    loading.value = true
    
    // Railway 서버 문제로 인해 기존 API만 사용 (실시간 엔드포인트 비활성화)
    console.log('✅ 기존 API를 사용하여 내전 데이터 로드 중...')
    const allTypes = ['soft', 'hard', 'hyper']
    let allMatches = []
    
    for (const type of allTypes) {
      try {
        console.log(`📡 ${type} 타입 내전 데이터 로드 중...`)
        const typeResponse = await fetch(`${API_BASE_URL}/matches/by-type/${type}`)
        if (typeResponse.ok) {
          const typeMatches = await typeResponse.json()
          allMatches = allMatches.concat(typeMatches)
          console.log(`✅ ${type} 타입: ${typeMatches.length}개 내전 로드 완료`)
        } else {
          console.warn(`⚠️ ${type} 타입 내전 로드 실패: ${typeResponse.status}`)
        }
      } catch (typeError) {
        console.warn(`❌ ${type} 타입 내전 로드 실패:`, typeError)
      }
    }
    
    // 활성 내전 필터링 (open과 in_progress 상태 모두 포함, 시간 제한 없음)
    const filteredMatches = allMatches.filter(match => {
      const isActive = match.status === 'open' || match.status === 'in_progress'
      console.log(`🔍 내전 ${match.customId}: 상태=${match.status}, 활성=${isActive}`)
      return isActive
    })
    
    realtimeMatches.value = filteredMatches
    
    // 디버깅을 위한 상세 로그
    console.log(`🎯 총 ${allMatches.length}개 내전 중 ${filteredMatches.length}개 활성 내전 표시`)
    console.log('📋 모든 내전 목록:', allMatches.map(m => ({
      customId: m.customId,
      status: m.status,
      createdAt: m.createdAt,
      type: m.type
    })))
    console.log('✅ 활성 내전 목록:', filteredMatches.map(m => ({
      customId: m.customId,
      status: m.status,
      createdAt: m.createdAt,
      type: m.type
    })))
    
    lastUpdated.value = new Date().toLocaleTimeString('ko-KR')
    
  } catch (error) {
    console.error('❌ 내전 데이터 로드 실패:', error)
    realtimeMatches.value = []
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  fetchRealtimeMatches()
}

const updateMatchStatus = async (matchId, newStatus) => {
  try {
    const response = await fetch(`${API_BASE_URL}/matches/${matchId}/status`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status: newStatus })
    })

    if (response.ok) {
      // 상태 업데이트 후 데이터 새로고침
      await fetchRealtimeMatches()
      alert(`내전 상태가 ${getStatusText(newStatus)}로 변경되었습니다.`)
    } else {
      throw new Error('상태 업데이트 실패')
    }
  } catch (error) {
    console.error('내전 상태 업데이트 실패:', error)
    alert('내전 상태 업데이트에 실패했습니다.')
  }
}

const viewMatch = (matchId) => {
  router.push(`/match/${matchId}`)
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

const formatTime = (timeString) => {
  const date = new Date(timeString)
  return date.toLocaleString('ko-KR', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
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

// 라이프사이클
onMounted(() => {
  // 알림 권한 요청
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission()
  }
  
  connectWebSocket()
  fetchRealtimeMatches()
  
  // 30초마다 자동 새로고침
  refreshInterval.value = setInterval(fetchRealtimeMatches, 30000)
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
  if (ws.value) {
    ws.value.close()
  }
})
</script>

<style scoped>
.realtime-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  position: relative;
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

.realtime-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 10px 15px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  backdrop-filter: blur(10px);
}

.status-indicator {
  padding: 6px 12px;
  border-radius: 15px;
  font-weight: bold;
  font-size: 0.9rem;
}

.status-indicator.connected {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
}

.status-indicator.disconnected {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
}

.status-indicator.polling {
  background: rgba(255, 152, 0, 0.2);
  color: #FF9800;
}

.realtime-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-radius: 15px;
  backdrop-filter: blur(10px);
}

.realtime-header h1 {
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

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.last-updated {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.matches-section, .stats-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 25px;
  margin-bottom: 25px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.matches-section h2, .stats-section h2 {
  color: #333;
  margin-bottom: 20px;
  font-size: 1.5rem;
  font-weight: bold;
}

.loading {
  text-align: center;
  padding: 40px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.no-matches {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.no-matches-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.matches-grid {
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

.type-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
}

.type-badge.soft {
  background: #e8f5e8;
  color: #4CAF50;
}

.type-badge.hard {
  background: #fff3e0;
  color: #FF9800;
}

.type-badge.hyper {
  background: #f3e5f5;
  color: #9C27B0;
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

.action-btn.complete {
  background: #e3f2fd;
  color: #2196F3;
}

.action-btn.close {
  background: #ffebee;
  color: #f44336;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 25px;
  border-radius: 15px;
  text-align: center;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon {
  font-size: 2.5rem;
  margin-bottom: 15px;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

@media (max-width: 768px) {
  .realtime-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .matches-grid {
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
