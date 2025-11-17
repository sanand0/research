import assert from 'node:assert/strict'
import { rankMatches } from '../web/static/viewer.js'

const items = [
  { text: 'The quick brown fox jumps over the lazy dog', page: 1 },
  { text: 'Another unrelated line', page: 2 },
  { text: 'Quick brown foxes leap fences', page: 3 },
]

const results = rankMatches(items, 'quik brown fxo', 2)
assert.equal(results.length, 2)
assert.ok(results[0].score <= results[1].score)
assert.ok(results[0].text.toLowerCase().includes('quick brown fox'))

console.log('search.spec.js passed')
