/**
 * Riot ID 텍스트에서 GameName#TagLine 추출 + 노이즈 필터링.
 * - 태그라인: ASCII 알파벳/숫자 2~5자 (KR1, KR03, 5499, ABC 등)
 * - 역할/배지/티어/기타 한글 토큰은 무시
 */
const ROLE_TOKENS = new Set([
  "TOP","JUNGLE","MID","ADC","SUPPORT","UNKNOWN","FILL",
  // 스샷 잡음(예: '부','돼','E' 등)은 여기서 필터
  "부","돼","E"
]);

// 한글 포함 이름 허용, 태그는 ASCII 2~5자만 허용해 '#원딜' 같은 오검출 방지
const RIOT_PAIR_RE = /([A-Za-z0-9\uac00-\ud7a3][A-Za-z0-9\uac00-\ud7a3 _.-]{0,15})#([A-Za-z0-9]{2,5})/g;

export type RiotId = { gameName: string; tagLine: string };

export function extractRiotIds(raw: string): RiotId[] {
  const out: RiotId[] = [];
  const seen = new Set<string>();
  let m: RegExpExecArray | null;
  while ((m = RIOT_PAIR_RE.exec(raw)) !== null) {
    const name = m[1].trim();
    const tag = m[2].toUpperCase().trim();
    // 배지/역할/티어 등 노이즈 라인일 확률이 높으면 스킵
    if (ROLE_TOKENS.has(name.toUpperCase())) continue;
    if (ROLE_TOKENS.has(tag.toUpperCase())) continue;
    // 길이/문자 제약(태그는 이미 정규식에서 필터)
    if (!name || tag.length < 2 || tag.length > 5) continue;

    const key = `${name}#${tag}`;
    if (!seen.has(key)) {
      seen.add(key);
      out.push({ gameName: name, tagLine: tag });
    }
  }
  return out;
}

/** 간단 전처리: 줄바꿈/배지 구분자로 쓰이는 특수문자 정리 */
export function normalizeSource(s: string) {
  return s
    .replace(/\u00A0/g, " ")        // nbsp
    .replace(/[|·•►▶]/g, " ")
    .replace(/\s{2,}/g, " ")
    .trim();
}
