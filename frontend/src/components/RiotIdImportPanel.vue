<script setup lang="ts">
import { ref } from "vue";
import Tesseract from "tesseract.js";
import { extractRiotIds, normalizeSource, type RiotId } from "../utils/parseRiotIds";
import { validateRiotIds, type ValidateResult } from "../utils/validateRiotIds";

const rawText = ref("");
const parsing = ref(false);
const validating = ref(false);
const ocring = ref(false);
const extracted = ref<RiotId[]>([]);
const validated = ref<ValidateResult[]>([]);
const error = ref<string | null>(null);

async function readClipboard() {
  error.value = null;
  try {
    // NOTE: HTTPS + 사용자 제스처 필요. 실패 시 textarea로 유도.
    const t = await navigator.clipboard.readText();
    rawText.value = t;
  } catch (e:any) {
    error.value = "클립보드 접근이 차단되었어요. 아래 텍스트 영역에 직접 붙여넣기 해주세요.";
  }
}

function parse() {
  parsing.value = true;
  try {
    const norm = normalizeSource(rawText.value);
    extracted.value = extractRiotIds(norm);
    if (extracted.value.length === 0) {
      error.value = "Riot ID를 찾지 못했어요. 이름#태그 형태인지 확인해주세요. (예: 오리좌#5499)";
    } else {
      error.value = null;
    }
  } finally {
    parsing.value = false;
  }
}

async function validateAll() {
  validating.value = true;
  try {
    validated.value = await validateRiotIds(extracted.value);
  } finally {
    validating.value = false;
  }
}

async function onImage(e: Event) {
  const files = (e.target as HTMLInputElement).files;
  if (!files?.length) return;
  const file = files[0];
  ocring.value = true; error.value = null;
  try {
    const { data } = await Tesseract.recognize(file, "eng+kor", { logger: () => {} });
    rawText.value = data.text || "";
    parse();
  } catch (e:any) {
    error.value = "OCR 중 오류가 발생했어요.";
  } finally {
    ocring.value = false;
  }
}

const emit = defineEmits<{
  (e: "done", list: RiotId[]): void
}>();

function proceed() {
  const ok = validated.value
    .filter(v => v.ok)
    .map(v => ({ gameName: v.gameName, tagLine: v.tagLine }));
  emit("done", ok);
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex gap-2">
      <button class="px-3 py-2 rounded bg-stone-800 text-white" @click="readClipboard">클립보드에서 불러오기</button>
      <label class="px-3 py-2 rounded bg-stone-700 text-white cursor-pointer">
        이미지(OCR) 업로드
        <input type="file" class="hidden" accept="image/*" @change="onImage" />
      </label>
    </div>

    <textarea v-model="rawText" rows="6" class="w-full border rounded p-2" placeholder="텍스트를 붙여넣기 하세요 (예: 오리좌#5499, 감바스바나나#KR2 ...)"></textarea>

    <div class="flex gap-2">
      <button class="px-3 py-2 rounded bg-black text-white" :disabled="parsing" @click="parse">
        {{ parsing ? "추출 중..." : "Riot ID 추출" }}
      </button>
      <button class="px-3 py-2 rounded bg-emerald-700 text-white" :disabled="!extracted.length || validating" @click="validateAll">
        {{ validating ? "검증 중..." : "라이엇 검증" }}
      </button>
    </div>

    <div v-if="error" class="text-red-600 text-sm">{{ error }}</div>

    <div v-if="extracted.length" class="text-sm">
      <div class="font-semibold mb-1">추출된 ID ({{ extracted.length }}):</div>
      <ul class="list-disc ml-5">
        <li v-for="(r,i) in extracted" :key="i">{{ r.gameName }}#{{ r.tagLine }}</li>
      </ul>
    </div>

    <div v-if="validated.length" class="text-sm">
      <div class="font-semibold mb-1">검증 결과:</div>
      <ul class="list-disc ml-5">
        <li v-for="(v,i) in validated" :key="i">
          <template v-if="v.ok">
            ✅ {{ v.gameName }}#{{ v.tagLine }} (valid)
          </template>
          <template v-else>
            ❌ {{ v.gameName }}#{{ v.tagLine }} — {{ v.reason }}
          </template>
        </li>
      </ul>
      <button class="mt-2 px-3 py-2 rounded bg-green-700 text-white" @click="proceed">유효한 ID로 진행</button>
    </div>

    <div v-if="ocring" class="text-xs text-stone-500">OCR 중...</div>
  </div>
</template>
