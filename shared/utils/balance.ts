import { Player, BalanceResult, Team } from '../types'

const TIER_SCORES: Record<string, number> = {
  IRON: 1, I: 1,
  BRONZE: 2, B: 2,
  SILVER: 3, S: 3,
  GOLD: 4, G: 4,
  PLATINUM: 5, P: 5,
  EMERALD: 6, E: 6,
  DIAMOND: 7, D: 7,
  MASTER: 8, M: 8,
  GRANDMASTER: 9, GM: 9,
  CHALLENGER: 10, C: 10,
  UNRANKED: 3, // Default to Silver
}

function getPlayerScore(player: Player): number {
  if (player.mmr) return player.mmr
  const tierScore = TIER_SCORES[player.tier?.toUpperCase() || 'UNRANKED'] || 3
  const rankScore = player.rank ? (5 - parseInt(player.rank, 10)) * 0.2 : 0
  return tierScore + rankScore
}

export function balanceTeams(players: Player[], options: { teamSize: number }): BalanceResult {
  const { teamSize = 5 } = options
  const numTeams = Math.floor(players.length / teamSize)
  if (numTeams < 2) {
    return { teams: [], qualityScore: 0 };
  }

  const scoredPlayers = players.map(p => ({ ...p, score: getPlayerScore(p) }))
    .sort((a, b) => b.score - a.score)

  const teams: Team[] = Array.from({ length: numTeams }, () => ({ players: [], totalScore: 0, lanes: {} }))

  // Distribute players using a greedy approach
  scoredPlayers.forEach(player => {
    const teamWithLowestScore = teams.sort((a, b) => a.totalScore - b.totalScore)[0]
    teamWithLowestScore.players.push(player)
    teamWithLowestScore.totalScore += player.score
  })

  const totalScores = teams.map(t => t.totalScore)
  const minScore = Math.min(...totalScores)
  const maxScore = Math.max(...totalScores)
  const qualityScore = 1 - (maxScore - minScore) / (maxScore || 1)

  return { teams, qualityScore }
}
