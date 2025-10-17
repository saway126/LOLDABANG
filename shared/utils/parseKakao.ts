import { Player } from '../types'

export function parseKakaoTalk(text: string): { players: Player[]; errors: string[] } {
  const lines = text.split('\n').filter((line) => line.trim() !== '')
  const players: Player[] = []
  const errors: string[] = []

  lines.forEach((line) => {
    try {
      const normalized = line.replace(/\s*\/\s*/g, '/').trim()
      const parts = normalized.split(/\s+/)
      const name = parts[0]
      const tierInfo = parts[1]
      const mainLane = parts[2]
      const preferredLanes = parts.slice(3)

      if (!name || !tierInfo || !mainLane) {
        throw new Error(`Incomplete line: ${line}`)
      }

      const tierMatch = tierInfo.match(/([a-zA-Z]+)(\d)/)
      const tier = tierMatch ? tierMatch[1].toUpperCase() : 'UNRANKED'
      const rank = tierMatch ? tierMatch[2] : ''

      players.push({
        name,
        tier,
        rank,
        mainLane: mainLane.toUpperCase(),
        preferredLanes: preferredLanes.map(l => l.toUpperCase()),
      })
    } catch (e) {
      errors.push(line)
    }
  })

  return { players, errors }
}
