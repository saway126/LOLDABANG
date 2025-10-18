<template>
  <div class="create">
    <div class="page-header">
      <h2 class="page-title">{{ isEditMode ? '✏️ 내전 수정' : '➕ 내전 생성' }}</h2>
      <p class="page-subtitle">{{ isEditMode ? '내전 정보를 수정하세요' : '카카오톡 댓글을 파싱하여 내전을 만들어보세요' }}</p>
    </div>
    
    <form @submit.prevent="createMatch" class="form-container">
      <div class="form-section">
        <h3 class="section-title">📝 내전 정보</h3>
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">내전 ID</label>
            <input 
              v-model="matchForm.customId" 
              type="text" 
              placeholder="예: 내전001"
              class="form-input"
              required
            />
          </div>
          
          <div class="form-group">
            <label class="form-label">진행자</label>
            <input 
              v-model="matchForm.host" 
              type="text" 
              placeholder="진행자 이름"
              class="form-input"
              required
            />
          </div>
          
          <div class="form-group">
            <label class="form-label">내전 종류</label>
            <select v-model="matchForm.type" class="form-select">
              <option value="soft">🟢 소프트 피어리스</option>
              <option value="hard">🟡 하드 피어리스</option>
              <option value="hyper">🔴 하이퍼 피어리스</option>
            </select>
          </div>
        </div>
      </div>
      
      <div class="form-section">
        <h3 class="section-title">💬 카카오톡 댓글 파싱</h3>
        <div class="parsing-container">
          <div class="form-group">
            <div class="form-label-row">
              <label class="form-label">댓글 텍스트 입력</label>
              <div class="input-buttons">
                <button type="button" @click="pasteFromClipboard" class="paste-btn">
                  📋 클립보드에서 붙여넣기
                </button>
                <button type="button" @click="triggerImageUpload" class="image-btn">
                  📷 이미지에서 추출
                </button>
                <input 
                  ref="imageInput" 
                  type="file" 
                  accept="image/*" 
                  @change="handleImageUpload" 
                  style="display: none"
                />
              </div>
            </div>
            <textarea 
              v-model="kakaoText"
              placeholder="닉네임#태그 G1 주라인 / 희망라인1 희망라인2&#10;예시:&#10;홍길동#KR1 G1 TOP / JUNGLE MID&#10;김철수#KR2 S2 JUNGLE / TOP"
              class="form-textarea"
              rows="6"
            ></textarea>
            <button type="button" @click="parseText" class="parse-btn" :disabled="ocrLoading">
              <span class="btn-icon">{{ ocrLoading ? '⏳' : '🔍' }}</span>
              <span class="btn-text">{{ ocrLoading ? 'OCR 처리 중...' : '파싱하기' }}</span>
            </button>
          </div>
        </div>
      </div>
      
      <div v-if="parsedPlayers.length > 0" class="form-section">
        <h3 class="section-title">👥 참가자 선택</h3>
        <div class="participants-container">
          <div class="participants-header">
            <span class="participants-count">{{ selectedPlayers.length }}명 선택됨</span>
            <button 
              type="button" 
              @click="toggleSelectAll"
              class="select-all-btn"
            >
              <span class="btn-icon">{{ selectedPlayers.length === parsedPlayers.length ? '☑️' : '☐' }}</span>
              <span class="btn-text">{{ selectedPlayers.length === parsedPlayers.length ? '전체 해제' : '전체 선택' }}</span>
            </button>
          </div>
          
          <div class="player-grid">
            <div 
              v-for="(player, index) in parsedPlayers" 
              :key="index"
              class="player-card"
              :class="{ 'selected': selectedPlayers.includes(player.name) }"
              @click="togglePlayer(player.name)"
            >
              <div class="player-checkbox">
                {{ selectedPlayers.includes(player.name) ? '☑️' : '☐' }}
              </div>
              <div class="player-info">
                <div class="player-name">{{ player.name }}</div>
                <div class="player-details">
                  <span class="player-tier">{{ player.tier }}{{ player.rank }}</span>
                  <span class="player-lane">{{ player.mainLane }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="form-actions">
        <button 
          type="submit" 
          :disabled="loading || selectedPlayers.length === 0"
          class="submit-btn"
        >
          <span class="btn-icon">{{ loading ? '⏳' : '🚀' }}</span>
          <span class="btn-text">{{ loading ? '생성 중...' : '내전 생성하기' }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'

// Tesseract.js 타입 선언
declare global {
  interface Window {
    Tesseract: any
  }
}

interface Player {
  name: string
  tier?: string
  rank?: string
  mainLane?: string
  preferredLanes?: string[]
}

const loading = ref(false)
const kakaoText = ref('')
const parsedPlayers = ref<Player[]>([])
const selectedPlayers = ref<string[]>([])
const imageInput = ref<HTMLInputElement | null>(null)
const ocrLoading = ref(false)

// 수정 모드 관련 변수들
const isEditMode = ref(false)
const editMatchId = ref<string | null>(null)
const originalMatchData = ref<any>(null)

// 환경에 따라 API URL 설정
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (import.meta.env.DEV 
    ? 'http://localhost:4000/api' 
    : 'https://loldabang-production.up.railway.app/api')

const matchForm = reactive({
  customId: '',
  host: '',
  type: 'soft' as 'soft' | 'hard' | 'hyper'
})

// 수정 모드 초기화
const initializeEditMode = async () => {
  const urlParams = new URLSearchParams(window.location.search)
  const editId = urlParams.get('edit')
  
  if (editId) {
    isEditMode.value = true
    editMatchId.value = editId
    
    try {
      // 기존 내전 데이터 로드
      const response = await fetch(`${API_BASE_URL}/matches/${editId}`)
      if (response.ok) {
        const matchData = await response.json()
        originalMatchData.value = matchData
        
        // 폼에 기존 데이터 설정
        matchForm.customId = matchData.customId
        matchForm.host = matchData.host
        matchForm.type = matchData.type
        
        // 기존 참가자 데이터 설정
        if (matchData.participants) {
          parsedPlayers.value = matchData.participants
          selectedPlayers.value = matchData.participants.map((p: any) => p.name)
        }
      } else {
        throw new Error('내전 데이터 로드 실패')
      }
    } catch (error) {
      console.error('수정 모드 초기화 실패:', error)
      alert('내전 데이터를 불러오는데 실패했습니다.')
      isEditMode.value = false
    }
  }
}

// 클립보드에서 텍스트 가져오기
const pasteFromClipboard = async () => {
  try {
    const text = await navigator.clipboard.readText()
    kakaoText.value = text
    // 자동으로 파싱도 실행
    parseText()
  } catch (err) {
    console.error('클립보드 접근 실패:', err)
    alert('클립보드 접근에 실패했습니다. 수동으로 붙여넣기 해주세요.')
  }
}

// 이미지 업로드 트리거
const triggerImageUpload = () => {
  imageInput.value?.click()
}

// Tesseract.js CDN 로드 함수 (간단한 방법)
const loadTesseract = async () => {
  return new Promise((resolve, reject) => {
    if (window.Tesseract) {
      resolve(window.Tesseract)
      return
    }
    
    // 가장 안정적인 CDN 사용
    const script = document.createElement('script')
    script.src = 'https://unpkg.com/tesseract.js@4.1.1/dist/tesseract.min.js'
    script.crossOrigin = 'anonymous'
    
    script.onload = () => {
      // 약간의 지연 후 Tesseract 확인
      setTimeout(() => {
        if (window.Tesseract) {
          console.log('Tesseract.js 로드 성공')
          resolve(window.Tesseract)
        } else {
          reject(new Error('Tesseract.js 로드 후에도 window.Tesseract가 없음'))
        }
      }, 500)
    }
    
    script.onerror = () => {
      reject(new Error('Tesseract.js CDN 로드 실패'))
    }
    
    document.head.appendChild(script)
  })
}

// 이미지 업로드 처리
const handleImageUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return
  
  // 이미지 파일 검증
  if (!file.type.startsWith('image/')) {
    alert('이미지 파일만 업로드 가능합니다.')
    return
  }
  
  ocrLoading.value = true
  
  try {
    // Tesseract.js CDN 로드
    const Tesseract = await loadTesseract() as any
    
    if (!Tesseract || !Tesseract.recognize) {
      throw new Error('Tesseract.js가 올바르게 로드되지 않았습니다.')
    }
    
    // 이미지를 Canvas로 변환
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    const img = new Image()
    
    img.crossOrigin = 'anonymous'
    
    img.onload = async () => {
      try {
        canvas.width = img.width
        canvas.height = img.height
        ctx?.drawImage(img, 0, 0)
        
        console.log('OCR 처리 시작...')
        
        // OCR 실행 (더 안정적인 설정)
        const result = await Tesseract.recognize(
          canvas.toDataURL('image/png'),
          'kor+eng', // 한국어 + 영어
          {
            logger: (m: any) => {
              if (m.status === 'recognizing text') {
                console.log(`OCR 진행률: ${Math.round(m.progress * 100)}%`)
              }
            }
            // Worker 경로는 자동으로 설정됨
          }
        )
        
        console.log('OCR 처리 완료:', result)
        
        // 추출된 텍스트를 textarea에 설정
        if (result && result.data && result.data.text) {
          kakaoText.value = result.data.text
          
          // 자동으로 파싱 실행
          parseText()
        } else {
          throw new Error('텍스트 추출에 실패했습니다.')
        }
        
      } catch (ocrError: any) {
        console.error('OCR 처리 중 오류:', ocrError)
        alert(`OCR 처리 실패: ${ocrError.message}`)
      } finally {
        ocrLoading.value = false
      }
    }
    
    img.src = URL.createObjectURL(file)
    
  } catch (error) {
    console.error('OCR 처리 실패:', error)
    alert('이미지에서 텍스트를 추출하는데 실패했습니다.')
    ocrLoading.value = false
  }
}

const parseKakaoTalk = (text: string): { players: Player[]; errors: string[] } => {
  const lines = text.split('\n').filter((line) => line.trim() !== '')
  const players: Player[] = []
  const errors: string[] = []

  lines.forEach((line) => {
    try {
      // 시간 정보 제거 (1시간 전, 55분 전 등)
      const timeRemoved = line.replace(/\d+\s*(시간|분|시간)\s*전/g, '').trim()
      
      // 정규화: 여러 공백을 하나로
      const normalized = timeRemoved.replace(/\s+/g, ' ')
      
      // 빈 라인 스킵
      if (!normalized) return
      
      // 닉네임#태그 패턴 찾기 (매우 유연하게)
      // 다양한 형식 지원: 닉네임#태그, 닉네임, 숫자@숫자 등
      let nameMatch = normalized.match(/^([^#\s]+(?:#[^\s]+)?)/)
      
      // 첫 번째 패턴이 실패하면 다른 패턴들 시도
      if (!nameMatch) {
        // 숫자@숫자 형식 (100@01)
        nameMatch = normalized.match(/^(\d+@\d+)/)
      }
      
      if (!nameMatch) {
        // 한글 닉네임만 있는 경우 (엄마지키는게임)
        nameMatch = normalized.match(/^([가-힣]+)/)
      }
      
      if (!nameMatch) {
        // 영문 닉네임만 있는 경우 (Evan)
        nameMatch = normalized.match(/^([A-Za-z]+)/)
      }
      
      if (!nameMatch) {
        // 시간 정보만 있는 라인은 스킵
        if (line.includes('시간') || line.includes('분')) return
        
        // 마지막 시도: 첫 번째 단어를 닉네임으로 사용
        const firstWord = normalized.split(' ')[0]
        if (firstWord && firstWord.length > 0) {
          nameMatch = [firstWord, firstWord]
        } else {
          throw new Error(`Invalid name format: ${line}`)
        }
      }
      
      const name = nameMatch[1]
      const remaining = normalized.substring(name.length).trim()
      
      // 티어 정보 추출 - OCR 오류 대응 패턴 (더 유연하게)
      const tierPattern = /^([A-Za-z]+)(\d*)\s*\/\s*([A-Za-z]+)(\d*)|^([A-Za-z]+)(\d*)|^\/\s*([A-Za-z]+)(\d*)\s*\/\s*([A-Za-z]+)(\d*)|^([A-Za-z]+)(\d*)\s*\/\s*([A-Za-z]+)(\d*)|^(\d+)\s*\/\s*(\d+)|^(\d+)|^([A-Za-z]+)|^([가-힣]+)(\d*)|^(\d+)\s*\/\s*(\d+)\s*\([^)]*\)/
      const tierMatch = remaining.match(tierPattern)
      
      // 티어 정보 추출
      let tier, rank
      if (!tierMatch) {
        // 티어 정보가 없으면 기본값 설정
        tier = 'UNRANKED'
        rank = ''
      } else {
        if (tierMatch[1] && tierMatch[2]) {
          // 현재티어/최고티어 형식 (E4/E4)
          tier = tierMatch[1].toUpperCase()
          rank = tierMatch[2]
        } else if (tierMatch[5] && tierMatch[6]) {
          // 단일 티어 형식 (G3)
          tier = tierMatch[5].toUpperCase()
          rank = tierMatch[6]
        } else if (tierMatch[7] && tierMatch[8]) {
          // /S4/S4 형식
          tier = tierMatch[7].toUpperCase()
          rank = tierMatch[8]
        } else if (tierMatch[9] && tierMatch[10]) {
          // m240/d2 형식 (소문자)
          tier = tierMatch[9].toUpperCase()
          rank = tierMatch[10]
        } else if (tierMatch[11] && tierMatch[12]) {
          // 숫자/숫자 형식 (63/03)
          tier = 'UNRANKED'
          rank = tierMatch[11]
        } else if (tierMatch[13]) {
          // 단일 숫자 형식
          tier = 'UNRANKED'
          rank = tierMatch[13]
        } else if (tierMatch[14]) {
          // 단일 문자 형식
          tier = tierMatch[14].toUpperCase()
          rank = ''
        } else if (tierMatch[15] && tierMatch[16]) {
          // 한글 티어 형식 (경쟁사 088)
          tier = 'UNRANKED'
          rank = tierMatch[16]
        } else if (tierMatch[17] && tierMatch[18]) {
          // 괄호 포함 숫자/숫자 형식 (63/03(임시))
          tier = 'UNRANKED'
          rank = tierMatch[17]
        } else {
          tier = 'UNRANKED'
          rank = ''
        }
      }
      
      // 티어 정보 제거
      const afterTier = remaining.replace(tierPattern, '').trim()
      
      // 라인 정보 추출 - 더 유연한 패턴
      console.log('After tier:', afterTier) // 디버깅용
      
      // 다양한 패턴을 시도
      let laneMatch = null
      let mainLane = 'UNKNOWN'
      let preferredLanes: string[] = []
      
      // 패턴 1: 주라인 / 희망라인 (정글/정글서폿)
      laneMatch = afterTier.match(/^\s*([가-힣ㅇ-ㅎㄱ-ㅎA-Za-z]+)\s*\/\s*(.+)/)
      if (laneMatch) {
        mainLane = laneMatch[1].trim()
        preferredLanes = laneMatch[2].split(/\s+/)
          .map(l => l.trim())
          .filter(l => l && l !== '/' && l !== '-')
      } else {
        // 패턴 2: / 주라인 / 희망라인 (/ 정글 / 정글 탑 서폿)
        laneMatch = afterTier.match(/^\s*\/\s*([가-힣ㅇ-ㅎㄱ-ㅎA-Za-z]+)\s*\/\s*(.+)/)
        if (laneMatch) {
          mainLane = laneMatch[1].trim()
          preferredLanes = laneMatch[2].split(/\s+/)
            .map(l => l.trim())
            .filter(l => l && l !== '/' && l !== '-')
        } else {
          // 패턴 3: 주라인만 (정글)
          laneMatch = afterTier.match(/^\s*([가-힣ㅇ-ㅎㄱ-ㅎA-Za-z]+)/)
          if (laneMatch) {
            mainLane = laneMatch[1].trim()
            preferredLanes = []
          } else {
            // 패턴 4: 공백으로 시작하는 주라인
            laneMatch = afterTier.match(/\s+([가-힣ㅇ-ㅎㄱ-ㅎA-Za-z]+)/)
            if (laneMatch) {
              mainLane = laneMatch[1].trim()
              preferredLanes = []
            }
          }
        }
      }
      
      console.log('Parsed lane - mainLane:', mainLane, 'preferredLanes:', JSON.stringify(preferredLanes)) // 디버깅용
      
      // 라인명 정규화 - 한글 자모 우선 매핑 (OCR 오류 대응)
      const laneMapping: Record<string, string> = {
        // 한글 자모 (우선순위 높음) - OCR 오류 패턴 포함
        'ㅇㄷ': 'ADC',      // 원딜
        'ㅅㅍ': 'SUPPORT',  // 서폿  
        'ㅁㄷ': 'MID',      // 미드
        'ㅈㄱ': 'JUNGLE',   // 정글
        'ㅌ': 'TOP',        // 탑
        'ㅁㄷㅇㄷ': 'MID ADC', // 미드원딜
        
        // 한글 풀네임
        '탑': 'TOP',
        '정글': 'JUNGLE', 
        '미드': 'MID',
        '원딜': 'ADC',
        '서폿': 'SUPPORT',
        
        // OCR 오류 패턴 (공백 포함)
        '정 글': 'JUNGLE',
        '미 드': 'MID',
        '원 딜': 'ADC',
        '서 폿': 'SUPPORT',
        '서 풋': 'SUPPORT',
        
        // OCR 오류 패턴 (자모 분리)
        'ㄷ ㄱ': 'JUNGLE',
        'ㅁ ㄷ': 'MID',
        'ㅇ ㄷ': 'ADC',
        'ㅅ ㅍ': 'SUPPORT',
        
        // 부분 매칭을 위한 키워드
        '서풋': 'SUPPORT',
        
        // 복합 라인명
        '정글서폿': 'JUNGLE SUPPORT',
        '정글탑': 'JUNGLE TOP',
        '미드탑': 'MID TOP',
        '원딜서폿': 'ADC SUPPORT',
        '서폿원딜': 'SUPPORT ADC'
      }
      
      // 메인 라인 정규화 (더 유연하게)
      mainLane = laneMapping[mainLane] || 
        Object.keys(laneMapping).find(key => mainLane.includes(key)) ? 
        laneMapping[Object.keys(laneMapping).find(key => mainLane.includes(key))!] : 
        mainLane.toUpperCase()
      
      const finalPreferredLanes = preferredLanes.map(l => {
        // 복합 라인명 처리
        if (l.includes('정글서폿')) return 'JUNGLE SUPPORT'
        if (l.includes('정글탑')) return 'JUNGLE TOP'
        if (l.includes('미드탑')) return 'MID TOP'
        if (l.includes('원딜서폿')) return 'ADC SUPPORT'
        if (l.includes('ㅁㄷㅇㄷ')) return 'MID ADC'
        
        // 부분 매칭 시도
        const partialMatch = Object.keys(laneMapping).find(key => l.includes(key))
        if (partialMatch) {
          return laneMapping[partialMatch]
        }
        
        return laneMapping[l] || l.toUpperCase()
      }).filter(l => l)
      
      console.log('Final result - name:', name, 'tier:', tier, 'rank:', rank, 'mainLane:', mainLane, 'preferredLanes:', JSON.stringify(finalPreferredLanes)) // 최종 결과
      
      // 희망 라인들 정규화
      preferredLanes = preferredLanes.map(l => {
        // 복합 라인명 처리
        if (l.includes('정글서폿')) return 'JUNGLE SUPPORT'
        if (l.includes('정글탑')) return 'JUNGLE TOP'
        if (l.includes('미드탑')) return 'MID TOP'
        if (l.includes('원딜서폿')) return 'ADC SUPPORT'
        if (l.includes('ㅁㄷㅇㄷ')) return 'MID ADC'
        
        return laneMapping[l] || l.toUpperCase()
      }).filter(l => l) // 빈 문자열 제거
      
      players.push({
        name,
        tier,
        rank,
        mainLane,
        preferredLanes,
      })
        } catch (e) {
          console.log('Parsing failed for line:', line, 'Error:', e)
          errors.push(line)
        }
  })

  return { players, errors }
}

const parseText = () => {
  const result = parseKakaoTalk(kakaoText.value)
  parsedPlayers.value = result.players
  selectedPlayers.value = result.players.map(p => p.name)
  
  if (result.errors.length > 0) {
    alert(`파싱에 실패한 라인: ${result.errors.join(', ')}`)
  }
}

const toggleSelectAll = () => {
  if (selectedPlayers.value.length === parsedPlayers.value.length) {
    selectedPlayers.value = []
  } else {
    selectedPlayers.value = parsedPlayers.value.map(p => p.name)
  }
}

const togglePlayer = (playerName: string) => {
  const index = selectedPlayers.value.indexOf(playerName)
  if (index > -1) {
    selectedPlayers.value.splice(index, 1)
  } else {
    selectedPlayers.value.push(playerName)
  }
}

const createMatch = async () => {
  if (!matchForm.customId || !matchForm.host || selectedPlayers.value.length === 0) {
    alert('모든 필드를 입력하고 참가자를 선택해주세요.')
    return
  }

  loading.value = true
  
  // 선택된 플레이어들의 전체 정보를 가져오기
  const selectedPlayerData = parsedPlayers.value.filter(player => 
    selectedPlayers.value.includes(player.name)
  )
  
  try {
    const url = isEditMode.value ? 
      `${API_BASE_URL}/matches/${editMatchId.value}` : 
      `${API_BASE_URL}/matches`
    
    const method = isEditMode.value ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...matchForm,
        participants: selectedPlayerData
      })
    })

    if (response.ok) {
      alert(isEditMode.value ? '내전이 성공적으로 수정되었습니다!' : '내전이 성공적으로 생성되었습니다!')
      
      if (!isEditMode.value) {
        // 생성 모드일 때만 폼 초기화
        Object.assign(matchForm, { customId: '', host: '', type: 'soft' })
        kakaoText.value = ''
        parsedPlayers.value = []
        selectedPlayers.value = []
      }
      
      // 홈페이지로 이동
      window.location.href = '/'
    } else {
      const error = await response.json()
      alert(error.message)
    }
  } catch (error) {
    alert('서버 오류가 발생했습니다.')
  } finally {
    loading.value = false
  }
}

// 컴포넌트 마운트 시 수정 모드 초기화
onMounted(() => {
  initializeEditMode()
})
</script>

<style scoped>
.create {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 1rem;
}

.page-header {
  text-align: center;
  margin-bottom: 2rem;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(139, 69, 19, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(212, 196, 168, 0.3);
}

.page-title {
  color: #8B4513;
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: bold;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
}

.page-subtitle {
  color: #A0522D;
  margin: 0;
  font-size: 1rem;
  opacity: 0.8;
}

.form-container {
  background: rgba(255, 255, 255, 0.9);
  padding: 2rem;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(139, 69, 19, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(212, 196, 168, 0.3);
}

.form-section {
  margin-bottom: 2.5rem;
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

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #8B4513;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 1rem;
  border: 2px solid #d4c4a8;
  border-radius: 12px;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.8);
  color: #8B4513;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #8B4513;
  box-shadow: 0 0 0 3px rgba(139, 69, 19, 0.1);
  background: rgba(255, 255, 255, 1);
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
  font-family: inherit;
}

.parsing-container {
  background: rgba(245, 241, 232, 0.5);
  padding: 1.5rem;
  border-radius: 15px;
  border: 1px solid rgba(212, 196, 168, 0.3);
}

.parse-btn {
  background: linear-gradient(135deg, #8B4513, #A0522D);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 12px;
  cursor: pointer;
  font-size: 1rem;
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(139, 69, 19, 0.3);
}

.parse-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(139, 69, 19, 0.4);
}

.btn-icon {
  font-size: 1.1rem;
}

.btn-text {
  font-weight: 500;
}

.participants-container {
  background: rgba(245, 241, 232, 0.5);
  padding: 1.5rem;
  border-radius: 15px;
  border: 1px solid rgba(212, 196, 168, 0.3);
}

.participants-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(212, 196, 168, 0.5);
}

.participants-count {
  color: #8B4513;
  font-weight: bold;
  font-size: 1.1rem;
}

.select-all-btn {
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid #d4c4a8;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  color: #8B4513;
  font-weight: 500;
}

.select-all-btn:hover {
  background: rgba(139, 69, 19, 0.1);
  border-color: #8B4513;
}

.player-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  max-height: 400px;
  overflow-y: auto;
  padding: 0.5rem;
}

.player-card {
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid #d4c4a8;
  border-radius: 12px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.player-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 69, 19, 0.2);
  border-color: #8B4513;
}

.player-card.selected {
  background: rgba(139, 69, 19, 0.1);
  border-color: #8B4513;
  box-shadow: 0 4px 12px rgba(139, 69, 19, 0.2);
}

.player-checkbox {
  font-size: 1.2rem;
  color: #8B4513;
}

.player-info {
  flex: 1;
}

.player-name {
  font-weight: bold;
  color: #8B4513;
  margin-bottom: 0.3rem;
  font-size: 1rem;
}

.player-details {
  display: flex;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.player-tier {
  background: rgba(139, 69, 19, 0.1);
  color: #8B4513;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  font-weight: 500;
}

.player-lane {
  background: rgba(160, 82, 45, 0.1);
  color: #A0522D;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  font-weight: 500;
}

.form-actions {
  text-align: center;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(212, 196, 168, 0.5);
}

.submit-btn {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  border: none;
  padding: 1.2rem 3rem;
  border-radius: 15px;
  cursor: pointer;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 auto;
  transition: all 0.3s ease;
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.3);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .player-grid {
    grid-template-columns: 1fr;
  }
  
  .participants-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .form-container {
    padding: 1.5rem;
  }
}

/* 클립보드 버튼 스타일 */
.form-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.input-buttons {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.paste-btn {
  background: linear-gradient(135deg, #8B4513, #A0522D);
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(139, 69, 19, 0.2);
}

.paste-btn:hover {
  background: linear-gradient(135deg, #A0522D, #8B4513);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(139, 69, 19, 0.3);
}

.image-btn {
  background: linear-gradient(135deg, #4A90E2, #357ABD);
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(74, 144, 226, 0.2);
}

.image-btn:hover {
  background: linear-gradient(135deg, #357ABD, #4A90E2);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(74, 144, 226, 0.3);
}

.parse-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}
</style>
