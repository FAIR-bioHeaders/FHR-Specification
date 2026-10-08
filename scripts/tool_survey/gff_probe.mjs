import { parseStringSync } from '@gmod/gff'
import { readFileSync } from 'fs'
const items = parseStringSync(readFileSync(process.argv[2], 'utf8'), { parseFeatures: true, parseComments: true, parseDirectives: true, parseSequences: true })
const k = items.map(i => Array.isArray(i) ? 'F:' + i[0].type : i.comment !== undefined ? 'C' : i.directive ? 'D:' + i.directive : i.sequence ? 'S:' + i.id : '?')
const c = {}; for (const x of k) c[x] = (c[x] || 0) + 1
console.log(JSON.stringify(c))
