<!-- 09ed71f4-5080-419d-a66d-0f5376241fa2 b4af815a-938c-4df4-804d-d4ac0f3506b5 -->
# Create.vue UI 실용적 개선 계획

## 목표
- 복잡한 카카오톡 파싱 로직 단순화로 오류율 감소
- Riot ID 가져오기 기능을 더 눈에 띄게 개선
- UI 중복 렌더링 문제 해결 (캐시 클리어)
- 불필요한 디버깅 콘솔 로그 제거

## 1단계: 카카오톡 파싱 로직 단순화

### frontend/src/views/Create.vue (384-626줄 수정)

**현재 문제점**:
- 너무 복잡한 정규표현식 (15개 이상의 조건 분기)
- OCR 오류 패턴 대응으로 인한 복잡도 증가
- 디버깅 콘솔 로그가 많음

**개선 방안**:

기본 패턴만 지원하는 단순한 파싱 함수로 교체:

```typescript
const parseKakaoTalk = (text: string): { players: Player[]; errors: string[] } => {
  const lines = text.split('\n').filter(line => line.trim() !== '')
  const players: Player[] = []
  const errors: string[] = []

  // 라인 매핑 (한글 -> 영문)
  const laneMap: Record<string, string> = {
    '탑': 'TOP', '정글': 'JUNGLE', '미드': 'MID',
    '원딜': 'ADC', '서폿': 'SUPPORT', '서풋': 'SUPPORT'
  }

  lines.forEach((line) => {
    try {
      // 시간 정보 제거
      const cleaned = line.replace(/\d+\s*(시간|분)\s*전/g, '').trim()
      if (!cleaned) return

      // 패턴 1: 닉네임#태그 티어 라인 형식
      // 예: "홍길동#KR1 G1 TOP"
      const pattern1 = /^([^#\s]+#[^\s]+)\s+([A-Z]+)(\d*)\s+([가-힣A-Z]+)/i
      const match1 = cleaned.match(pattern1)
      
      if (match1) {
        const [, name, tier, rank, lane] = match1
        players.push({
          name: name.trim(),
          tier: tier.toUpperCase(),
          rank: rank || '',
          mainLane: laneMap[lane] || lane.toUpperCase(),
          preferredLanes: []
        })
        return
      }

      // 패턴 2: 닉네임#태그 티어 / 라인 형식
      // 예: "홍길동#KR1 G1 / TOP JUNGLE"
      const pattern2 = /^([^#\s]+#[^\s]+)\s+([A-Z]+)(\d*)\s+\/\s+(.+)/i
      const match2 = cleaned.match(pattern2)
      
      if (match2) {
        const [, name, tier, rank, lanes] = match2
        const laneList = lanes.split(/\s+/).map(l => laneMap[l] || l.toUpperCase())
        players.push({
          name: name.trim(),
          tier: tier.toUpperCase(),
          rank: rank || '',
          mainLane: laneList[0] || 'UNKNOWN',
          preferredLanes: laneList.slice(1)
        })
        return
      }

      // 패턴 3: 닉네임만 (간단한 형식)
      // 예: "홍길동#KR1"
      const pattern3 = /^([^#\s]+#[^\s]+)/
      const match3 = cleaned.match(pattern3)
      
      if (match3) {
        players.push({
          name: match3[1].trim(),
          tier: 'UNRANKED',
          rank: '',
          mainLane: 'UNKNOWN',
          preferredLanes: []
        })
        return
      }

      // 파싱 실패
      throw new Error('지원하지 않는 형식')
      
    } catch (e) {
      errors.push(line)
    }
  })

  return { players, errors }
}
```

**변경 사항**:
- 3가지 기본 패턴만 지원
- OCR 오류 패턴 제거 (Riot ID 가져오기 권장)
- 디버깅 콘솔 로그 모두 제거 (493, 532, 598줄)
- 복잡한 티어 패턴 제거 (437-487줄)

## 2단계: Riot ID 가져오기 UI 개선

### frontend/src/views/Create.vue (45-55줄 수정)

**현재 상태**: details 태그로 접혀있음

**개선 방안**:

```vue
<div class="form-section riot-import-section">
  <h3 class="section-title">⭐ Riot ID 가져오기 (추천)</h3>
  <div class="riot-import-highlight">
    <div class="import-description">
      <p>📌 가장 정확한 방법입니다!</p>
      <p>클립보드, 이미지 OCR, 또는 직접 입력으로 Riot ID를 가져올 수 있습니다.</p>
    </div>
    <RiotIdImportPanel @done="onRiotIdImport" />
  </div>
</div>
```

**CSS 추가** (1086줄 뒤):

```css
.riot-import-section {
  background: linear-gradient(135deg, rgba(139, 69, 19, 0.08), rgba(212, 196, 168, 0.15));
  padding: 2rem;
  border-radius: 15px;
  border: 2px solid rgba(139, 69, 19, 0.3);
}

.riot-import-highlight {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(139, 69, 19, 0.1);
}

.import-description {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: rgba(74, 144, 226, 0.05);
  border-left: 4px solid #4A90E2;
  border-radius: 8px;
}

.import-description p {
  margin: 0.5rem 0;
  color: #333;
  font-size: 0.95rem;
}

.import-description p:first-child {
  font-weight: 600;
  color: #4A90E2;
}
```

## 3단계: 카카오톡 파싱 섹션 개선

### frontend/src/views/Create.vue (57-91줄 수정)

**변경 사항**:
- 섹션 제목에 "선택사항" 표시 추가
- placeholder 텍스트 단순화

```vue
<div class="form-section">
  <h3 class="section-title">💬 카카오톡 댓글 파싱 (선택사항)</h3>
  <div class="parsing-note">
    <p>⚠️ 간단한 형식만 지원합니다. 복잡한 경우 Riot ID 가져오기를 사용하세요.</p>
    <p>지원 형식: <code>닉네임#태그 G1 TOP</code> 또는 <code>닉네임#태그 G1 / TOP JUNGLE</code></p>
  </div>
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
        placeholder="홍길동#KR1 G1 TOP&#10;김철수#KR2 P4 / JUNGLE MID&#10;이영희#KR3 S2 ADC"
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
```

**CSS 추가** (1086줄 뒤):

```css
.parsing-note {
  background: rgba(255, 193, 7, 0.1);
  border-left: 4px solid #FFC107;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 8px;
}

.parsing-note p {
  margin: 0.5rem 0;
  font-size: 0.9rem;
  color: #666;
}

.parsing-note code {
  background: rgba(139, 69, 19, 0.1);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  color: #8B4513;
}
```

## 4단계: 오류 메시지 개선

### frontend/src/views/Create.vue (628-636줄 수정)

**변경 사항**:
- 더 자세한 오류 메시지 제공

```typescript
const parseText = () => {
  if (!kakaoText.value.trim()) {
    alert('텍스트를 입력해주세요.')
    return
  }

  const result = parseKakaoTalk(kakaoText.value)
  parsedPlayers.value = result.players
  selectedPlayers.value = result.players.map(p => p.name)
  
  if (result.players.length === 0 && result.errors.length > 0) {
    alert('❌ 파싱에 실패했습니다.\n\n지원 형식:\n• 닉네임#태그 G1 TOP\n• 닉네임#태그 P4 / JUNGLE MID\n\n복잡한 경우 "Riot ID 가져오기"를 사용하세요.')
  } else if (result.errors.length > 0) {
    alert(`✅ ${result.players.length}명 파싱 성공\n⚠️ ${result.errors.length}개 라인 실패\n\n실패한 라인:\n${result.errors.slice(0, 3).join('\n')}${result.errors.length > 3 ? '\n...' : ''}`)
  } else {
    alert(`✅ ${result.players.length}명 성공적으로 파싱되었습니다!`)
  }
}
```

## 5단계: 빌드 및 배포

1. 프론트엔드 빌드: `cd frontend && npm run build`
2. Vercel 배포: `vercel --prod`
3. Git 커밋 및 푸시

## 예상 결과

1. **Riot ID 가져오기가 더 눈에 띔**: 하이라이트 박스, 추천 배지
2. **카카오톡 파싱이 단순하고 명확**: 3가지 기본 패턴만 지원
3. **오류 메시지 개선**: 사용자가 무엇이 잘못됐는지 명확히 알 수 있음
4. **콘솔 스팸 제거**: 디버깅 로그 모두 제거
5. **UI 중복 문제 해결**: 빌드 재생성으로 캐시 클리어


### To-dos

- [ ] 카카오톡 파싱 로직을 3가지 기본 패턴만 지원하도록 단순화
- [ ] 디버깅 콘솔 로그 모두 제거 (493, 532, 598줄)
- [ ] Riot ID 가져오기 섹션을 펼쳐진 상태로 변경하고 하이라이트 스타일 적용
- [ ] 카카오톡 파싱 섹션에 지원 형식 안내 추가
- [ ] parseText 함수의 오류 메시지 개선 (더 자세하고 친절하게)
- [ ] 새로운 UI 요소에 대한 CSS 스타일 추가
- [ ] 프론트엔드 빌드 및 Vercel 배포, Git 커밋/푸시