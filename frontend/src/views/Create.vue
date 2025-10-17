<template>
  <div class="create">
    <h2>내전 생성</h2>
    
    <form @submit.prevent="createMatch" class="form">
      <div class="form-group">
        <label>내전 ID</label>
        <input 
          v-model="matchForm.customId" 
          type="text" 
          placeholder="예: 내전001"
          required
        />
      </div>
      
      <div class="form-group">
        <label>진행자</label>
        <input 
          v-model="matchForm.host" 
          type="text" 
          placeholder="진행자 이름"
          required
        />
      </div>
      
      <div class="form-group">
        <label>내전 종류</label>
        <select v-model="matchForm.type">
          <option value="soft">소프트 피어리스</option>
          <option value="hard">하드 피어리스</option>
          <option value="hyper">하이퍼 피어리스</option>
        </select>
      </div>
      
      <div class="form-group">
        <label>카톡 댓글 텍스트</label>
        <textarea 
          v-model="kakaoText"
          placeholder="닉네임#태그 G1 주라인 / 희망라인1 희망라인2"
          rows="4"
        ></textarea>
        <button type="button" @click="parseText" class="parse-btn">파싱</button>
      </div>
      
      <div v-if="parsedPlayers.length > 0" class="form-group">
        <label>참가자 선택 ({{ selectedPlayers.length }}명 선택됨)</label>
        <div class="player-list">
          <button 
            type="button" 
            @click="toggleSelectAll"
            class="select-all-btn"
          >
            {{ selectedPlayers.length === parsedPlayers.length ? '전체 해제' : '전체 선택' }}
          </button>
          
          <div 
            v-for="(player, index) in parsedPlayers" 
            :key="index"
            class="player-item"
            @click="togglePlayer(player.name)"
          >
            <span class="checkbox">
              {{ selectedPlayers.includes(player.name) ? '☑️' : '☐' }}
            </span>
            <span class="player-text">
              {{ player.name }} ({{ player.tier }}{{ player.rank }}) - {{ player.mainLane }}
            </span>
          </div>
        </div>
      </div>
      
      <button 
        type="submit" 
        :disabled="loading || selectedPlayers.length === 0"
        class="submit-btn"
      >
        {{ loading ? '생성 중...' : '내전 생성' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

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

const matchForm = reactive({
  customId: '',
  host: '',
  type: 'soft' as 'soft' | 'hard' | 'hyper'
})

const parseKakaoTalk = (text: string): { players: Player[]; errors: string[] } => {
  const lines = text.split('\n').filter((line) => line.trim() !== '')
  const players: Player[] = []
  const errors: string[] = []

  lines.forEach((line) => {
    try {
      // 정규화: 여러 공백을 하나로
      const normalized = line.trim().replace(/\s+/g, ' ')
      
      // 닉네임#태그 패턴 찾기
      // 닉네임#태그 형식 매칭 - 공백 허용
      const nameMatch = normalized.match(/^([^#]+#[^\s]+)/)
      if (!nameMatch) {
        throw new Error(`Invalid name format: ${line}`)
      }
      
      const name = nameMatch[1]
      const remaining = normalized.substring(name.length).trim()
      
      // 티어 정보 추출 - 더 유연한 패턴
      const tierPattern = /^([A-Za-z]+)(\d*)\s*\/\s*([A-Za-z]+)(\d*)|^([A-Za-z]+)(\d*)|^\/\s*([A-Za-z]+)(\d*)\s*\/\s*([A-Za-z]+)(\d*)|^([A-Za-z]+)(\d*)\s*\/\s*([A-Za-z]+)(\d*)/
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
      
      // 라인명 정규화 - 한글 자모 우선 매핑
      const laneMapping: Record<string, string> = {
        // 한글 자모 (우선순위 높음)
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
        
        // 복합 라인명
        '정글서폿': 'JUNGLE SUPPORT',
        '정글탑': 'JUNGLE TOP',
        '미드탑': 'MID TOP',
        '원딜서폿': 'ADC SUPPORT',
        '서폿원딜': 'SUPPORT ADC'
      }
      
      // 메인 라인 정규화
      mainLane = laneMapping[mainLane] || mainLane.toUpperCase()
      
      const finalPreferredLanes = preferredLanes.map(l => {
        if (l.includes('정글서폿')) return 'JUNGLE SUPPORT'
        if (l.includes('정글탑')) return 'JUNGLE TOP'
        if (l.includes('미드탑')) return 'MID TOP'
        if (l.includes('원딜서폿')) return 'ADC SUPPORT'
        if (l.includes('ㅁㄷㅇㄷ')) return 'MID ADC'
        
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
    const response = await fetch('http://localhost:4000/api/matches', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...matchForm,
        participants: selectedPlayerData
      })
    })

    if (response.ok) {
      alert('내전이 성공적으로 생성되었습니다!')
      // 폼 초기화
      Object.assign(matchForm, { customId: '', host: '', type: 'soft' })
      kakaoText.value = ''
      parsedPlayers.value = []
      selectedPlayers.value = []
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
</script>

<style scoped>
.create {
  max-width: 600px;
  margin: 0 auto;
}

.create h2 {
  color: #333;
  margin-bottom: 1.5rem;
}

.form {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group textarea {
  resize: vertical;
}

.parse-btn {
  background: #2196F3;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 0.5rem;
}

.player-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.select-all-btn {
  width: 100%;
  padding: 0.5rem;
  border: none;
  background: #f5f5f5;
  cursor: pointer;
  font-weight: bold;
  color: #2196F3;
}

.player-item {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  border-bottom: 1px solid #eee;
  cursor: pointer;
}

.player-item:hover {
  background: #f9f9f9;
}

.checkbox {
  margin-right: 0.5rem;
}

.submit-btn {
  width: 100%;
  background: #4CAF50;
  color: white;
  border: none;
  padding: 1rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
