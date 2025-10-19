<!-- 09ed71f4-5080-419d-a66d-0f5376241fa2 34bde7e1-3a0a-41f0-aa5a-29d63d8364cf -->
# 밸런싱 결과 투명성 개선 계획

## 현재 상황 분석

### 밸런스 조율 페이지 (Balance.vue)

- **점수 계산 방식**: 티어만 기반 (443-450줄)
  ```javascript
  const tierScores = {
    'CHALLENGER': 10, 'GRANDMASTER': 9, 'MASTER': 8,
    'DIAMOND': 7, 'PLATINUM': 6, 'GOLD': 5,
    'SILVER': 4, 'BRONZE': 3, 'IRON': 2, 'UNRANKED': 1
  }
  ```

- **결과 표시**: "팀 점수 5.0", "품질 점수 100%" (128줄)
- **문제점**: 각 플레이어가 몇 점인지, 왜 이렇게 나눴는지 불명확

### 라이엇 밸런싱 페이지 (RiotBalance.vue)

- **점수 계산 방식**: 백엔드 API 호출 (backend/services/balance.py)
  - 랭크 점수 70% (Iron 0 ~ Challenger 1900)
  - 승률 보너스 30% (50% 기준 ±40점/10%p)
- **결과 표시**: 티어, LP, 승률, 최종 점수 표시 (200-210줄)
- **장점**: 점수 기준표가 이미 있음 (52-172줄)

## 개선 계획

### 1단계: Balance.vue 결과 화면 상세화

#### A. 개별 플레이어 점수 표시 추가

**frontend/src/views/Balance.vue** (141-148줄 수정)

현재:

```vue
<div class="player-info">
  <div class="player-name">{{ player.name }}</div>
  <div class="player-details">
    <span :class="['tier-badge', getTierClass(player.tier)]">
      {{ player.tier || 'UNRANKED' }}{{ player.rank || '' }}
    </span>
```

수정:

```vue
<div class="player-info">
  <div class="player-name-row">
    <div class="player-name">{{ player.name }}</div>
    <div class="player-score">{{ getPlayerScore(player) }}점</div>
  </div>
  <div class="player-details">
    <span :class="['tier-badge', getTierClass(player.tier)]">
      {{ player.tier || 'UNRANKED' }}{{ player.rank || '' }}
    </span>
```

#### B. 점수 계산 함수 추가

**frontend/src/views/Balance.vue** (500줄 뒤에 추가)

```javascript
const getPlayerScore = (player: Player): number => {
  const tierScores: Record<string, number> = {
    'CHALLENGER': 10, 'GRANDMASTER': 9, 'MASTER': 8,
    'DIAMOND': 7, 'PLATINUM': 6, 'GOLD': 5,
    'SILVER': 4, 'BRONZE': 3, 'IRON': 2, 'UNRANKED': 1
  }
  return tierScores[player.tier] || 1
}
```

#### C. 점수 기준표 모달 추가

**frontend/src/views/Balance.vue** (109줄 뒤에 추가)

```vue
<div v-if="balanceResult" class="balance-result">
  <div class="result-header">
    <h3 class="result-title">🎯 밸런싱 결과</h3>
    <button @click="showScoreGuide = !showScoreGuide" class="score-guide-btn">
      📊 점수 기준표
    </button>
    <div class="quality-score">
```

점수 기준표 모달 (balanceResult 섹션 상단):

```vue
<div v-if="showScoreGuide" class="score-guide-modal" @click="showScoreGuide = false">
  <div class="score-guide-content" @click.stop>
    <h4>📊 티어별 점수 기준</h4>
    <table class="score-table">
      <tr><td>Challenger</td><td>10점</td></tr>
      <tr><td>Grandmaster</td><td>9점</td></tr>
      <tr><td>Master</td><td>8점</td></tr>
      <tr><td>Diamond</td><td>7점</td></tr>
      <tr><td>Platinum</td><td>6점</td></tr>
      <tr><td>Gold</td><td>5점</td></tr>
      <tr><td>Silver</td><td>4점</td></tr>
      <tr><td>Bronze</td><td>3점</td></tr>
      <tr><td>Iron</td><td>2점</td></tr>
      <tr><td>Unranked</td><td>1점</td></tr>
    </table>
    <p class="guide-note">* 팀 점수 = 각 플레이어 점수의 합</p>
    <p class="guide-note">* 품질 점수 = 1 - |팀1점수 - 팀2점수| / 총점</p>
    <button @click="showScoreGuide = false" class="close-btn">닫기</button>
  </div>
</div>
```

#### D. 팀별 비교 시각화 추가

**frontend/src/views/Balance.vue** (119줄 뒤에 추가)

```vue
<div class="result-header">
  <!-- ... 기존 코드 ... -->
</div>

<!-- 팀 비교 차트 추가 -->
<div class="team-comparison">
  <div class="comparison-bar">
    <div class="team1-bar" :style="{ width: getTeamPercentage(0) + '%' }">
      팀 1: {{ balanceResult.teams[0].totalScore.toFixed(1) }}점
    </div>
    <div class="team2-bar" :style="{ width: getTeamPercentage(1) + '%' }">
      팀 2: {{ balanceResult.teams[1].totalScore.toFixed(1) }}점
    </div>
  </div>
  <div class="comparison-diff">
    점수 차이: {{ Math.abs(balanceResult.teams[0].totalScore - balanceResult.teams[1].totalScore).toFixed(1) }}점
  </div>
</div>

<div class="teams-container">
```

비율 계산 함수:

```javascript
const getTeamPercentage = (teamIndex: number): number => {
  if (!balanceResult.value) return 50
  const totalScore = balanceResult.value.teams[0].totalScore + balanceResult.value.teams[1].totalScore
  return (balanceResult.value.teams[teamIndex].totalScore / totalScore) * 100
}
```

### 2단계: RiotBalance.vue 결과 화면 개선

#### A. 팀별 통계 요약 추가

**frontend/src/views/RiotBalance.vue** (193-219줄 수정)

현재 팀 표시 전에 통계 추가:

```vue
<div v-if="diff !== null" class="text-sm">팀 점수 차이(낮을수록 균형): <b>{{ diff?.toFixed(1) }}</b></div>

<!-- 팀 통계 요약 추가 -->
<div class="team-stats-summary">
  <div class="stat-card">
    <h5>팀 A 통계</h5>
    <p>평균 점수: {{ getAverageScore(teamA).toFixed(1) }}</p>
    <p>평균 티어: {{ getAverageTier(teamA) }}</p>
    <p>평균 승률: {{ getAverageWinrate(teamA) }}</p>
  </div>
  <div class="stat-card">
    <h5>팀 B 통계</h5>
    <p>평균 점수: {{ getAverageScore(teamB).toFixed(1) }}</p>
    <p>평균 티어: {{ getAverageTier(teamB) }}</p>
    <p>평균 승률: {{ getAverageWinrate(teamB) }}</p>
  </div>
</div>

<div class="grid grid-cols-1 md:grid-cols-2 gap-4" v-if="teamA.length || teamB.length">
```

통계 계산 함수들:

```javascript
const getAverageScore = (team: PlayerOut[]): number => {
  if (!team.length) return 0
  return team.reduce((sum, p) => sum + p.score, 0) / team.length
}

const getAverageTier = (team: PlayerOut[]): string => {
  const tierValues = { IRON: 1, BRONZE: 2, SILVER: 3, GOLD: 4, PLATINUM: 5, 
                       EMERALD: 6, DIAMOND: 7, MASTER: 8, GRANDMASTER: 9, CHALLENGER: 10 }
  const avg = team.reduce((sum, p) => sum + (tierValues[p.tier] || 0), 0) / team.length
  const tiers = Object.entries(tierValues).sort((a, b) => a[1] - b[1])
  return tiers.find(([_, v]) => v >= avg)?.[0] || 'UNRANKED'
}

const getAverageWinrate = (team: PlayerOut[]): string => {
  const withWR = team.filter(p => p.winrate != null)
  if (!withWR.length) return '데이터 없음'
  const avg = withWR.reduce((sum, p) => sum + p.winrate!, 0) / withWR.length
  return (avg * 100).toFixed(0) + '%'
}
```

### 3단계: CSS 스타일 추가

#### Balance.vue 스타일

**frontend/src/views/Balance.vue** (650줄 뒤에 추가)

```css
.player-name-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.player-score {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--primary-color);
  background: rgba(139, 69, 19, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.score-guide-btn {
  padding: 0.5rem 1rem;
  background: rgba(139, 69, 19, 0.1);
  border: 1px solid var(--primary-color);
  border-radius: 8px;
  color: var(--primary-color);
  cursor: pointer;
  transition: all 0.3s;
}

.score-guide-btn:hover {
  background: var(--primary-color);
  color: white;
}

.score-guide-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.score-guide-content {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.score-table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

.score-table td {
  padding: 0.5rem;
  border-bottom: 1px solid #eee;
}

.score-table td:first-child {
  font-weight: 600;
}

.score-table td:last-child {
  text-align: right;
  color: var(--primary-color);
}

.guide-note {
  font-size: 0.875rem;
  color: #666;
  margin: 0.5rem 0;
}

.team-comparison {
  margin: 1.5rem 0;
  padding: 1rem;
  background: rgba(139, 69, 19, 0.05);
  border-radius: 8px;
}

.comparison-bar {
  display: flex;
  height: 40px;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.team1-bar, .team2-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: white;
}

.team1-bar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.team2-bar {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.comparison-diff {
  text-align: center;
  font-size: 0.875rem;
  color: #666;
  font-weight: 600;
}
```

#### RiotBalance.vue 스타일

**frontend/src/views/RiotBalance.vue** (끝에 추가)

```css
.team-stats-summary {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin: 1rem 0;
}

.stat-card {
  padding: 1rem;
  background: rgba(139, 69, 19, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(139, 69, 19, 0.2);
}

.stat-card h5 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: var(--primary-color);
}

.stat-card p {
  font-size: 0.875rem;
  margin: 0.5rem 0;
  color: #666;
}
```

### 4단계: 반응형 변수 추가

**frontend/src/views/Balance.vue** (168-170줄 뒤에)

```javascript
const showScoreGuide = ref(false)
```

## 구현 순서

1. Balance.vue에 개별 플레이어 점수 표시 추가
2. Balance.vue에 점수 기준표 모달 추가  
3. Balance.vue에 팀 비교 시각화 추가
4. RiotBalance.vue에 팀 통계 요약 추가
5. CSS 스타일 추가 (Balance.vue, RiotBalance.vue)
6. 반응형 변수 및 함수 추가
7. 빌드 및 테스트
8. 배포

## 예상 결과

### 밸런스 조율 페이지

- 각 플레이어 옆에 "5점", "7점" 등 개별 점수 표시
- "점수 기준표" 버튼으로 티어별 점수 기준 확인 가능
- 팀1 vs 팀2 점수 비교 바 차트
- 점수 차이 명시

### 라이엇 밸런싱 페이지  

- 각 팀의 평균 점수, 평균 티어, 평균 승률 요약
- 개별 플레이어 점수는 이미 표시됨
- 점수 기준표는 이미 있음

플레이어들이 "왜 이렇게 나눴는지" 명확히 알 수 있어 밸런싱 결과를 납득할 수 있습니다.

### To-dos

- [ ] RealtimeBanPick.vue의 fetchActiveMatches() 함수에서 404 오류나는 /api/matches/realtime 엔드포인트를 타입별 API 호출로 수정
- [ ] 폴링 모드 표시 텍스트를 '5초마다'에서 '30초마다'로 수정 (Realtime.vue, RealtimeBanPick.vue)
- [ ] style.css에 브라운/베이지 테마 CSS 변수 정의 추가 (:root)
- [ ] Realtime.vue의 보라색 그라데이션을 CSS 변수 기반 브라운 테마로 변경
- [ ] RealtimeBanPick.vue의 보라색 그라데이션을 CSS 변수 기반 브라운 테마로 변경
- [ ] Balance.vue의 보라색 그라데이션을 CSS 변수 기반 브라운 테마로 변경
- [ ] 빈 상태 메시지의 이모지 크기 줄이고 스타일 개선 (모든 페이지)
- [ ] 모든 액션 버튼에 일관된 브라운 테마 스타일 적용
- [ ] 프론트엔드 빌드 및 Vercel 배포