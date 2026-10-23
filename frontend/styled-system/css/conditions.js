import { withoutSpace } from '../helpers';

const conditions = /* @__PURE__ */ new Set(/* @__PURE__ */ "base".split(','))
const conditionRe = /^@|&/
const underscoreRe = /^_/
const selectorRe = /&|@/

export const breakpointKeys = ["base"]

export function isCondition(v) {
  return conditions.has(v) || conditionRe.test(v)
}

export function finalizeConditions(paths) {
  return paths.map((p) => {
    if (conditions.has(p)) {
      return p.replace(underscoreRe, '')
    }
    if (selectorRe.test(p)) {
      return `[${withoutSpace(p.trim())}]`
    }
    return p
  })
}

export function sortConditions(paths) {
  return [...paths].sort((a, b) => {
    const aa = isCondition(a)
    const bb = isCondition(b)
    return aa && !bb ? 1 : !aa && bb ? -1 : 0
  })
}