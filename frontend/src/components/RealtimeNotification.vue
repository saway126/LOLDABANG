<template>
  <div class="notification-container">
    <!-- 알림 토글 버튼 -->
    <div class="notification-toggle">
      <button 
        @click="toggleNotifications" 
        class="toggle-btn"
        :class="{ active: showNotifications }"
        :title="unreadCount > 0 ? `읽지 않은 알림 ${unreadCount}개` : '알림'"
      >
        <span class="bell-icon">🔔</span>
        <span v-if="unreadCount > 0" class="unread-badge">
          {{ unreadCount > 99 ? '99+' : unreadCount }}
        </span>
      </button>
    </div>

    <!-- 알림 패널 -->
    <div v-if="showNotifications" class="notification-panel">
      <div class="panel-header">
        <h3>알림</h3>
        <div class="panel-actions">
          <button @click="markAllAsRead" class="mark-all-btn" v-if="unreadCount > 0">
            모두 읽음
          </button>
          <button @click="clearAllNotifications" class="clear-all-btn" v-if="notifications.length > 0">
            모두 삭제
          </button>
          <button @click="toggleSettings" class="settings-btn">
            ⚙️
          </button>
        </div>
      </div>
      
      <div class="notifications-list" v-if="notifications.length > 0">
        <div 
          v-for="notification in notifications" 
          :key="notification.id"
          class="notification-item"
          :class="[getNotificationClass(notification.type), { unread: !notification.read }]"
          @click="markAsRead(notification.id)"
        >
          <div class="notification-icon">
            {{ getNotificationIcon(notification.type) }}
          </div>
          <div class="notification-content">
            <div class="notification-title">
              {{ notification.title || getNotificationTitle(notification.type) }}
            </div>
            <div class="notification-message">
              {{ notification.message }}
            </div>
            <div class="notification-time">
              {{ formatTime(notification.timestamp) }}
            </div>
          </div>
          <div class="notification-actions">
            <button @click.stop="removeNotification(notification.id)" class="close-btn">
              ✕
            </button>
          </div>
        </div>
      </div>
      
      <div v-else class="no-notifications">
        <div class="no-notifications-icon">🔕</div>
        <p>새로운 알림이 없습니다</p>
      </div>
    </div>

    <!-- 알림 설정 모달 -->
    <div v-if="showSettings" class="notification-settings-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>알림 설정</h3>
          <button @click="showSettings = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <div class="setting-item">
            <label>
              <input 
                type="checkbox" 
                v-model="settings.matchStatusUpdates"
              />
              내전 상태 변경 알림
            </label>
          </div>
          <div class="setting-item">
            <label>
              <input 
                type="checkbox" 
                v-model="settings.adminNotifications"
              />
              관리자 알림
            </label>
          </div>
          <div class="setting-item">
            <label>
              <input 
                type="checkbox" 
                v-model="settings.banPickUpdates"
              />
              밴픽 업데이트 알림
            </label>
          </div>
          <div class="setting-item">
            <label>
              <input 
                type="checkbox" 
                v-model="settings.soundEnabled"
              />
              소리 알림
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="saveSettings" class="save-btn">저장</button>
          <button @click="showSettings = false" class="cancel-btn">취소</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// 반응형 데이터
const notifications = ref([])
const showNotifications = ref(false)
const showSettings = ref(false)
const settings = ref({
  matchStatusUpdates: true,
  adminNotifications: true,
  banPickUpdates: true,
  soundEnabled: true
})

// 읽지 않은 알림 개수
const unreadCount = computed(() => {
  return notifications.value.filter(n => !n.read).length
})

// WebSocket 연결 (Railway WebSocket 지원 문제로 비활성화)
const ws = ref(null)
const isConnected = ref(false)

// WebSocket 연결 시도 (선택적)
const connectWebSocket = () => {
  try {
    ws.value = new WebSocket(import.meta.env.VITE_WS_URL || 'wss://loldabang-production.up.railway.app/ws')
    
    ws.value.onopen = () => {
      isConnected.value = true
      console.log('✅ 알림 WebSocket 연결됨')
    }
    
    ws.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handleWebSocketMessage(data)
      } catch (error) {
        console.error('❌ WebSocket 메시지 파싱 오류:', error)
      }
    }
    
    ws.value.onclose = () => {
      isConnected.value = false
      console.log('🔴 알림 WebSocket 연결 끊김')
    }
    
    ws.value.onerror = (error) => {
      isConnected.value = false
      console.warn('⚠️ WebSocket 연결 실패 (Railway WebSocket 미지원 가능)')
    }
  } catch (error) {
    console.warn('⚠️ WebSocket 초기화 실패:', error)
  }
}

const send = (message) => {
  if (ws.value && ws.value.readyState === WebSocket.OPEN) {
    ws.value.send(JSON.stringify(message))
  }
}


// 메서드
const handleWebSocketMessage = (data) => {
  switch (data.type) {
    case 'match_status_update':
      if (settings.value.matchStatusUpdates) {
        addNotification({
          type: 'match_status',
          message: `${data.custom_id} 내전이 ${getStatusText(data.new_status)}로 변경되었습니다.`,
          timestamp: data.timestamp,
          data: data
        })
      }
      break
    case 'admin_notification':
      if (settings.value.adminNotifications) {
        addNotification({
          type: 'admin',
          message: data.message,
          timestamp: data.timestamp,
          priority: data.priority || 'normal',
          data: data
        })
      }
      break
    case 'banpick_update':
      if (settings.value.banPickUpdates) {
        addNotification({
          type: 'banpick',
          message: `${data.match_id} 내전의 밴픽이 업데이트되었습니다.`,
          timestamp: data.timestamp,
          data: data
        })
      }
      break
  }
}

const addNotification = (notification) => {
  const newNotification = {
    id: Date.now() + Math.random(),
    type: notification.type,
    message: notification.message,
    timestamp: notification.timestamp,
    read: false,
    priority: notification.priority || 'normal',
    data: notification.data
  }
  
  notifications.value.unshift(newNotification)
  
  // 최대 50개까지만 유지
  if (notifications.value.length > 50) {
    notifications.value = notifications.value.slice(0, 50)
  }
  
  // 소리 알림
  if (settings.value.soundEnabled) {
    playNotificationSound()
  }
  
  // 자동으로 5초 후 읽음 처리
  setTimeout(() => {
    markAsRead(newNotification.id)
  }, 5000)
}

const playNotificationSound = () => {
  try {
    const audio = new Audio('/sounds/notification.mp3')
    audio.volume = 0.3
    audio.play().catch(() => {
      // 오디오 재생 실패 시 무시
    })
  } catch (error) {
    // 오디오 파일이 없거나 재생 실패 시 무시
  }
}

const markAsRead = (notificationId) => {
  const notification = notifications.value.find(n => n.id === notificationId)
  if (notification) {
    notification.read = true
  }
}

const removeNotification = (notificationId) => {
  const index = notifications.value.findIndex(n => n.id === notificationId)
  if (index > -1) {
    notifications.value.splice(index, 1)
  }
}

const toggleNotifications = () => {
  showNotifications.value = !showNotifications.value
}

const markAllAsRead = () => {
  notifications.value.forEach(notification => {
    notification.read = true
  })
}

const clearAllNotifications = () => {
  notifications.value = []
}

const toggleSettings = () => {
  showSettings.value = !showSettings.value
}

const getNotificationClass = (type) => {
  return {
    'notification-match': type === 'match_status',
    'notification-admin': type === 'admin',
    'notification-banpick': type === 'banpick'
  }
}

const getNotificationIcon = (type) => {
  const icons = {
    'match_status': '🎮',
    'admin': '📢',
    'banpick': '⚔️'
  }
  return icons[type] || '🔔'
}

const getNotificationTitle = (type) => {
  const titles = {
    'match_status': '내전 상태 변경',
    'admin': '관리자 알림',
    'banpick': '밴픽 업데이트'
  }
  return titles[type] || '알림'
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

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) { // 1분 미만
    return '방금 전'
  } else if (diff < 3600000) { // 1시간 미만
    return `${Math.floor(diff / 60000)}분 전`
  } else if (diff < 86400000) { // 1일 미만
    return `${Math.floor(diff / 3600000)}시간 전`
  } else {
    return date.toLocaleDateString('ko-KR')
  }
}

const saveSettings = () => {
  localStorage.setItem('notificationSettings', JSON.stringify(settings.value))
  showSettings.value = false
}

const loadSettings = () => {
  const saved = localStorage.getItem('notificationSettings')
  if (saved) {
    settings.value = { ...settings.value, ...JSON.parse(saved) }
  }
}

// 라이프사이클
onMounted(() => {
  loadSettings()
  // WebSocket 연결 시도 (Railway 지원 문제로 선택적)
  // connectWebSocket()
})

// 키보드 단축키
const handleKeydown = (event) => {
  if (event.ctrlKey && event.key === 'n') {
    event.preventDefault()
    toggleNotifications()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

// 컴포넌트 외부에서 사용할 수 있도록 함수들을 expose
defineExpose({
  addNotification,
  removeNotification,
  markAsRead,
  markAllAsRead,
  clearAllNotifications
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.notification-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
}

.notifications-list {
  position: absolute;
  top: 60px;
  right: 0;
  width: 350px;
  max-height: 500px;
  overflow-y: auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  border: 1px solid #e0e0e0;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  padding: 15px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.notification-item:hover {
  background: #f8f9fa;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-item.notification-match {
  border-left: 4px solid #4CAF50;
}

.notification-item.notification-admin {
  border-left: 4px solid #FF9800;
}

.notification-item.notification-banpick {
  border-left: 4px solid #2196F3;
}

.notification-icon {
  font-size: 1.5rem;
  margin-right: 12px;
  margin-top: 2px;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
  font-size: 0.9rem;
}

.notification-message {
  color: #666;
  font-size: 0.85rem;
  line-height: 1.4;
  margin-bottom: 4px;
}

.notification-time {
  color: #999;
  font-size: 0.75rem;
}

.notification-actions {
  margin-left: 8px;
}

.close-btn {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  font-size: 1rem;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #f0f0f0;
  color: #666;
}

.notification-toggle {
  position: relative;
}

.toggle-btn {
  background: rgba(139, 69, 19, 0.1);
  border: 1px solid rgba(139, 69, 19, 0.2);
  color: var(--primary-color);
  padding: 8px 12px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.3s ease;
  position: relative;
  min-width: 40px;
  height: 36px;
}

.toggle-btn:hover {
  background: rgba(139, 69, 19, 0.2);
  transform: translateY(-1px);
}

.toggle-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}


.unread-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: var(--error-color);
  color: white;
  border-radius: 50%;
  min-width: 18px;
  height: 18px;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  padding: 0 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

/* 알림 패널 */
.notification-panel {
  position: absolute;
  top: 50px;
  right: 0;
  width: 350px;
  max-height: 500px;
  background: white;
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  border: 1px solid rgba(139, 69, 19, 0.1);
  z-index: 1000;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid rgba(139, 69, 19, 0.1);
  background: rgba(139, 69, 19, 0.03);
}

.panel-header h3 {
  margin: 0;
  color: var(--primary-color);
  font-size: 1.1rem;
}

.panel-actions {
  display: flex;
  gap: 8px;
}

.mark-all-btn, .clear-all-btn, .settings-btn {
  background: none;
  border: 1px solid rgba(139, 69, 19, 0.2);
  color: var(--primary-color);
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mark-all-btn:hover, .clear-all-btn:hover, .settings-btn:hover {
  background: rgba(139, 69, 19, 0.1);
}

.no-notifications {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.no-notifications-icon {
  font-size: 2rem;
  margin-bottom: 10px;
  opacity: 0.6;
}

.notification-item.unread {
  background: rgba(139, 69, 19, 0.03);
  border-left: 4px solid var(--primary-color);
}

.notification-settings-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 400px;
  max-width: 90vw;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.modal-body {
  padding: 20px;
}

.setting-item {
  margin-bottom: 15px;
}

.setting-item label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 0.9rem;
  color: #333;
}

.setting-item input[type="checkbox"] {
  margin-right: 10px;
  width: 16px;
  height: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #e0e0e0;
}

.save-btn, .cancel-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.2s ease;
}

.save-btn {
  background: #4CAF50;
  color: white;
}

.save-btn:hover {
  background: #45a049;
}

.cancel-btn {
  background: #f0f0f0;
  color: #666;
}

.cancel-btn:hover {
  background: #e0e0e0;
}

@media (max-width: 768px) {
  .notification-container {
    top: 10px;
    right: 10px;
  }
  
  .notifications-list {
    width: 300px;
    max-height: 400px;
  }
  
  .notification-item {
    padding: 12px;
  }
  
  .toggle-btn {
    width: 45px;
    height: 45px;
    font-size: 1.1rem;
  }
}
</style>
