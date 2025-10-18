import { ref, onMounted, onUnmounted } from 'vue'

export function useWebSocket(url, options = {}) {
  const ws = ref(null)
  const isConnected = ref(false)
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = options.maxReconnectAttempts || 5
  const reconnectInterval = options.reconnectInterval || 3000

  const connect = () => {
    try {
      ws.value = new WebSocket(url)
      
      ws.value.onopen = () => {
        isConnected.value = true
        reconnectAttempts.value = 0
        console.log('WebSocket 연결됨')
        options.onOpen?.()
      }
      
      ws.value.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          options.onMessage?.(data)
        } catch (error) {
          console.error('WebSocket 메시지 파싱 오류:', error)
        }
      }
      
      ws.value.onclose = (event) => {
        isConnected.value = false
        console.log('WebSocket 연결 끊김:', event.code, event.reason)
        options.onClose?.(event)
        
        // 자동 재연결 시도
        if (reconnectAttempts.value < maxReconnectAttempts) {
          reconnectAttempts.value++
          console.log(`재연결 시도 ${reconnectAttempts.value}/${maxReconnectAttempts}`)
          setTimeout(connect, reconnectInterval)
        } else {
          console.error('최대 재연결 시도 횟수 초과')
          options.onMaxReconnectAttempts?.()
        }
      }
      
      ws.value.onerror = (error) => {
        console.error('WebSocket 오류:', error)
        options.onError?.(error)
      }
    } catch (error) {
      console.error('WebSocket 연결 실패:', error)
      options.onError?.(error)
    }
  }

  const disconnect = () => {
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
    isConnected.value = false
  }

  const send = (data) => {
    if (ws.value && isConnected.value) {
      try {
        ws.value.send(JSON.stringify(data))
        return true
      } catch (error) {
        console.error('WebSocket 메시지 전송 실패:', error)
        return false
      }
    }
    return false
  }

  const ping = () => {
    send({ type: 'ping' })
  }

  onMounted(() => {
    connect()
  })

  onUnmounted(() => {
    disconnect()
  })

  return {
    ws,
    isConnected,
    connect,
    disconnect,
    send,
    ping
  }
}
