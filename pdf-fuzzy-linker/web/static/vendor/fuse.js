// Minimal fuzzy matcher compatible with Fuse.js API
export default class Fuse {
  constructor(list, options = {}) {
    this.list = list
    this.keys = options.keys || []
    this.threshold = options.threshold ?? 0.6
  }

  search(pattern, opts = {}) {
    const limit = opts.limit ?? this.list.length
    const lowerPattern = pattern.toLowerCase()
    const scored = this.list.map((item, index) => {
      const haystack = this.keys.length ? this.keys.map((k) => String(item[k] ?? '')).join(' ') : String(item)
      const lowerHaystack = haystack.toLowerCase()
      const distance = levenshtein(lowerPattern, lowerHaystack)
      const scale = Math.max(lowerPattern.length, lowerHaystack.length, 1)
      return { item, score: distance / scale, index }
    })
    scored.sort((a, b) => a.score - b.score)
    const filtered = scored.filter((entry) => entry.score <= this.threshold)
    const chosen = (filtered.length ? filtered : scored).slice(0, limit)
    return chosen.map((entry) => ({ item: entry.item, score: entry.score, refIndex: entry.index }))
  }
}

function levenshtein(a, b) {
  const dp = Array.from({ length: a.length + 1 }, () => new Array(b.length + 1).fill(0))
  for (let i = 0; i <= a.length; i += 1) dp[i][0] = i
  for (let j = 0; j <= b.length; j += 1) dp[0][j] = j
  for (let i = 1; i <= a.length; i += 1) {
    for (let j = 1; j <= b.length; j += 1) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1
      dp[i][j] = Math.min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    }
  }
  return dp[a.length][b.length]
}
