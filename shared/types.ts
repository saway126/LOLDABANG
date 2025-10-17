export interface Player {
  id?: number
  name: string
  tier?: string
  rank?: string
  mainLane?: string
  preferredLanes?: string[]
  mmr?: number
}

export interface Match {
  id: number
  customId: string
  host: string
  type: 'soft' | 'hard' | 'hyper'
  status: string
  createdAt: string
}

export interface Participant {
  matchId: number
  playerId: number
  status: 'waiting' | 'confirmed'
}

export interface Team {
    players: Player[];
    totalScore: number;
    lanes: Record<string, Player | null>;
}

export interface BalanceResult {
    teams: Team[];
    qualityScore: number;
}
