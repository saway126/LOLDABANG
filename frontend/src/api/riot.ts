export async function fetchRiotBalance(payload: {
  players: { gameName: string; tagLine: string; platform?: string }[];
  recent?: number;
}) {
  const res = await fetch(`${import.meta.env.VITE_API_BASE || ""}/api/riot/balance-5v5`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ recent: payload.recent ?? 8, players: payload.players }),
  });
  if (!res.ok) throw new Error(`API Error ${res.status}`);
  return await res.json();
}
