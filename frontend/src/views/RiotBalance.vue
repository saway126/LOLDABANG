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
</script>

<template>
  <div class="p-6 space-y-6">
    <h1 class="text-2xl font-bold">Riot 점수 기반 5v5 밸런싱</h1>

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
