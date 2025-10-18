<template>
  <div class="notification-container">
    <!-- 알림 목록 -->
    <div class="notifications-list" v-if="notifications.length > 0">
      <div 
        v-for="notification in notifications" 
        :key="notification.id"
        class="notification-item"
        :class="getNotificationClass(notification.type)"
        @click="markAsRead(notification.id)"
      >
        <div class="notification-icon">
          {{ getNotificationIcon(notification.type) }}
        </div>
        <div class="notification-content">
          <div class="notification-title">
            {{ getNotificationTitle(notification.type) }}
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

    <!-- 알림 토글 버튼 -->
    <div class="notification-toggle">
      <button 
        @click="toggleNotifications" 
        class="toggle-btn"
        :class="{ active: showNotifications }"
      >
        🔔
        <span v-if="unreadCount > 0" class="unread-badge">
          {{ unreadCount }}
        </span>
      </button>
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
import { useWebSocket } from '../composables/useWebSocket'

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

// WebSocket 연결
const { isConnected, send } = useWebSocket(
  import.meta.env.VITE_WS_URL || 'wss://loldabang-production.up.railway.app/ws',
  {
    onMessage: handleWebSocketMessage,
    onOpen: () => {
      console.log('알림 WebSocket 연결됨')
    },
    onClose: () => {
      console.log('알림 WebSocket 연결 끊김')
    }
  }
)

// 계산된 속성
const unreadCount = computed(() => {
  return notifications.value.filter(n => !n.read).length
})

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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  position: relative;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.toggle-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.toggle-btn.active {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
}

.unread-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ff4444;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
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
