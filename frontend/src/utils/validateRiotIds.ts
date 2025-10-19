/**
 * 서버 프락시를 통해 Riot Account API 검증.
 * 백엔드에 /api/riot/account/by-riot-id?gameName=..&tagLine=.. 같은 프락시가 있다고 가정.
 * 없으면 해당 경로만 만들어주거나 이 함수의 fetch URL을 맞게 바꾸세요.
 */
export type ValidateResult =
  { ok: true; gameName: string; tagLine: string; puuid: string } |
  { ok: false; gameName: string; tagLine: string; reason: string };

export async function validateRiotIds(ids: {gameName:string; tagLine:string}[]): Promise<ValidateResult[]> {
  const results: ValidateResult[] = [];
  for (const id of ids) {
    try {
      const url = `${import.meta.env.VITE_API_BASE || ""}/api/riot/account/by-riot-id?gameName=${encodeURIComponent(id.gameName)}&tagLine=${encodeURIComponent(id.tagLine)}`;
      const r = await fetch(url);
      if (!r.ok) {
        results.push({ ok:false, gameName:id.gameName, tagLine:id.tagLine, reason:`HTTP ${r.status}` });
        continue;
      }
      const data = await r.json(); // { puuid, gameName, tagLine } 형태라고 가정
      if (data?.puuid) {
        results.push({ ok:true, gameName:data.gameName || id.gameName, tagLine:data.tagLine || id.tagLine, puuid:data.puuid });
      } else {
        results.push({ ok:false, gameName:id.gameName, tagLine:id.tagLine, reason:"invalid" });
      }
    } catch (e:any) {
      results.push({ ok:false, gameName:id.gameName, tagLine:id.tagLine, reason:e?.message || "network error" });
    }
  }
  return results;
}
