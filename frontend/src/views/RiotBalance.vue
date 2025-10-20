<script setup lang="ts">
import { ref } from "vue";
import { fetchRiotBalance } from "../api/riot";

type Player = { gameName: string; tagLine: string; platform?: string };
type PlayerOut = { gameName: string; tagLine: string; tier?: string; rank?: string; lp: number; winrate?: number; score: number };

const players = ref<Player[]>([
  { gameName: "소환사1", tagLine: "KR1", platform: "KR" },
  { gameName: "소환사2", tagLine: "KR1", platform: "KR" },
  { gameName: "소환사3", tagLine: "KR1", platform: "KR" },
  { gameName: "소환사4", tagLine: "KR1", platform: "KR" },
  { gameName: "소환사5", tagLine: "KR1", platform: "KR" },
  { gameName: "소환사6", tagLine: "KR1", platform: "KR" },
  { gameName: "소환사7", tagLine: "KR1", platform: "KR" },
  { gameName: "소환사8", tagLine: "KR1", platform: "KR" },
  { gameName: "소환사9", tagLine: "KR1", platform: "KR" },
  { gameName: "소환사10", tagLine: "KR1", platform: "KR" },
]);

const recent = ref(8);
const loading = ref(false);
const error = ref<string | null>(null);
const teamA = ref<PlayerOut[]>([]);
const teamB = ref<PlayerOut[]>([]);
const diff = ref<number | null>(null);
const showScoreGuide = ref(false);

async function runBalance() {
  try {
    loading.value = true; error.value = null;
    const res = await fetchRiotBalance({ players: players.value, recent: recent.value });
    teamA.value = res.teamA; teamB.value = res.teamB; diff.value = res.diff;
  } catch (e:any) {
    error.value = e?.message || String(e);
  } finally {
    loading.value = false;
  }
}

const getAverageScore = (team: PlayerOut[]): number => {
  if (!team.length) return 0
  return team.reduce((sum, p) => sum + p.score, 0) / team.length
}

const getAverageTier = (team: PlayerOut[]): string => {
  const tierValues = { IRON: 1, BRONZE: 2, SILVER: 3, GOLD: 4, PLATINUM: 5, 
                       EMERALD: 6, DIAMOND: 7, MASTER: 8, GRANDMASTER: 9, CHALLENGER: 10 }
  const avg = team.reduce((sum, p) => sum + (tierValues[p.tier as keyof typeof tierValues] || 0), 0) / team.length
  const tiers = Object.entries(tierValues).sort((a, b) => a[1] - b[1])
  return tiers.find(([_, v]) => v >= avg)?.[0] || 'UNRANKED'
}

const getAverageWinrate = (team: PlayerOut[]): string => {
  const withWR = team.filter(p => p.winrate != null)
  if (!withWR.length) return '데이터 없음'
  const avg = withWR.reduce((sum, p) => sum + p.winrate!, 0) / withWR.length
  return (avg * 100).toFixed(0) + '%'
}
</script>

<template>
  <div class="p-6 space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">Riot 점수 기반 5v5 밸런싱</h1>
      <button @click="showScoreGuide = !showScoreGuide" class="px-4 py-2 rounded bg-blue-500 text-white hover:bg-blue-600 transition-colors">
        {{ showScoreGuide ? '기준표 닫기' : '점수 기준표 보기' }}
      </button>
    </div>

    <!-- 점수 기준표 -->
    <div v-if="showScoreGuide" class="bg-white rounded-lg shadow-lg p-6 border-2 border-blue-200">
      <h2 class="text-xl font-bold mb-4 text-center">📊 점수 계산 기준표</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- 랭크 점수 (70%) -->
        <div>
          <h3 class="text-lg font-semibold mb-3 text-blue-600">🏆 랭크 점수 (70%)</h3>
          <div class="space-y-2">
            <div class="flex justify-between items-center p-2 bg-gray-50 rounded">
              <span class="font-medium">Iron</span>
              <span class="text-gray-600">0점</span>
            </div>
            <div class="flex justify-between items-center p-2 bg-orange-100 rounded">
              <span class="font-medium">Bronze</span>
              <span class="text-orange-600">200점</span>
            </div>
            <div class="flex justify-between items-center p-2 bg-gray-100 rounded">
              <span class="font-medium">Silver</span>
              <span class="text-gray-600">400점</span>
            </div>
            <div class="flex justify-between items-center p-2 bg-yellow-100 rounded">
              <span class="font-medium">Gold</span>
              <span class="text-yellow-600">600점</span>
            </div>
            <div class="flex justify-between items-center p-2 bg-green-100 rounded">
              <span class="font-medium">Platinum</span>
              <span class="text-green-600">800점</span>
            </div>
            <div class="flex justify-between items-center p-2 bg-emerald-100 rounded">
              <span class="font-medium">Emerald</span>
              <span class="text-emerald-600">1000점</span>
            </div>
            <div class="flex justify-between items-center p-2 bg-blue-100 rounded">
              <span class="font-medium">Diamond</span>
              <span class="text-blue-600">1200점</span>
            </div>
            <div class="flex justify-between items-center p-2 bg-purple-100 rounded">
              <span class="font-medium">Master</span>
              <span class="text-purple-600">1500점</span>
            </div>
            <div class="flex justify-between items-center p-2 bg-pink-100 rounded">
              <span class="font-medium">Grandmaster</span>
              <span class="text-pink-600">1700점</span>
            </div>
            <div class="flex justify-between items-center p-2 bg-red-100 rounded">
              <span class="font-medium">Challenger</span>
              <span class="text-red-600">1900점</span>
            </div>
          </div>
          
          <div class="mt-4 p-3 bg-blue-50 rounded">
            <h4 class="font-semibold text-sm mb-2">디비전 보너스</h4>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div class="flex justify-between">
                <span>IV</span>
                <span>+0점</span>
              </div>
              <div class="flex justify-between">
                <span>III</span>
                <span>+50점</span>
              </div>
              <div class="flex justify-between">
                <span>II</span>
                <span>+100점</span>
              </div>
              <div class="flex justify-between">
                <span>I</span>
                <span>+150점</span>
              </div>
            </div>
          </div>
          
          <div class="mt-3 p-3 bg-green-50 rounded">
            <h4 class="font-semibold text-sm mb-2">LP 보너스</h4>
            <div class="text-sm space-y-1">
              <div>• Iron~Diamond: 최대 100점</div>
              <div>• Master~Challenger: 최대 300점</div>
            </div>
          </div>
        </div>

        <!-- 승률 보너스 (30%) -->
        <div>
          <h3 class="text-lg font-semibold mb-3 text-green-600">📈 승률 보너스 (30%)</h3>
          <div class="space-y-3">
            <div class="p-4 bg-green-50 rounded">
              <h4 class="font-semibold text-sm mb-2">기준: 50% 승률</h4>
              <div class="text-sm space-y-1">
                <div>• 승률 10%p 차이당 40점 보너스</div>
                <div>• 예: 60% 승률 = +40점</div>
                <div>• 예: 40% 승률 = -40점</div>
              </div>
            </div>
            <div class="p-4 bg-yellow-50 rounded">
              <h4 class="font-semibold text-sm mb-2">가중 방식</h4>
              <div class="text-sm space-y-1">
                <div>• 최근 승률 = 솔랭 70% + 자랭 30% 가중 평균</div>
                <div>• 둘 중 하나만 있으면 해당 큐 승률만 사용</div>
              </div>
            </div>
            
            <div class="p-4 bg-blue-50 rounded">
              <h4 class="font-semibold text-sm mb-2">최근 경기 수</h4>
              <div class="text-sm space-y-1">
                <div>• 기본: 8경기</div>
                <div>• 최대: 20경기</div>
                <div>• 경기 수가 적을수록 부정확할 수 있음</div>
              </div>
            </div>
            
            <div class="p-4 bg-yellow-50 rounded">
              <h4 class="font-semibold text-sm mb-2">최종 점수 계산</h4>
              <div class="text-sm space-y-1">
                <div>• 랭크 점수 × 0.7</div>
                <div>• 승률 보너스 × 0.3</div>
                <div>• 두 값을 합산하여 최종 점수</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="mt-6 p-4 bg-gray-100 rounded text-center">
        <p class="text-sm text-gray-600">
          💡 <strong>팁:</strong> 팀 점수 차이가 낮을수록 더 균형잡힌 팀 구성입니다!
        </p>
      </div>
    </div>

    <div class="flex items-center gap-4">
      <label class="font-medium">최근 경기 수</label>
      <input type="number" v-model.number="recent" min="1" max="20" class="border rounded px-2 py-1 w-24" />
      <button @click="runBalance" class="px-4 py-2 rounded bg-black text-white" :disabled="loading">
        {{ loading ? "계산 중..." : "밸런싱 실행" }}
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <h2 class="text-xl font-semibold">입력(10명)</h2>
        <div v-for="(p, i) in players" :key="i" class="flex gap-2 mb-2">
          <input v-model="p.gameName" placeholder="gameName" class="border rounded px-2 py-1 w-40" />
          <input v-model="p.tagLine"  placeholder="tagLine"  class="border rounded px-2 py-1 w-28" />
          <input v-model="p.platform"  placeholder="KR"       class="border rounded px-2 py-1 w-20" />
        </div>
      </div>

      <div v-if="error" class="text-red-600">에러: {{ error }}</div>
      <div v-else class="space-y-3">
        <div v-if="diff !== null" class="text-sm">팀 점수 차이(낮을수록 균형): <b>{{ diff?.toFixed(1) }}</b></div>

        <!-- 팀 통계 요약 -->
        <div class="team-stats-summary" v-if="teamA.length || teamB.length">
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
          <div>
            <h3 class="font-semibold">팀 A</h3>
            <ul class="text-sm space-y-1">
              <li v-for="(p, i) in teamA" :key="i">
                {{ p.gameName }}#{{ p.tagLine }} — {{ p.tier ?? "UNRANKED" }} {{ p.rank ?? "" }}
                (LP {{ p.lp }}, WR {{ p.winrate != null ? (p.winrate*100).toFixed(0)+'%' : '-' }}, S {{ p.score.toFixed(1) }})
              </li>
            </ul>
          </div>
          <div>
            <h3 class="font-semibold">팀 B</h3>
            <ul class="text-sm space-y-1">
              <li v-for="(p, i) in teamB" :key="i">
                {{ p.gameName }}#{{ p.tagLine }} — {{ p.tier ?? "UNRANKED" }} {{ p.rank ?? "" }}
                (LP {{ p.lp }}, WR {{ p.winrate != null ? (p.winrate*100).toFixed(0)+'%' : '-' }}, S {{ p.score.toFixed(1) }})
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
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
  color: var(--primary-color, #8b4513);
}

.stat-card p {
  font-size: 0.875rem;
  margin: 0.5rem 0;
  color: #666;
}

@media (max-width: 768px) {
  .team-stats-summary {
    grid-template-columns: 1fr;
  }
}
</style>
