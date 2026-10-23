import { createAssignCss, createMergeCss, createSerializeCss, createSerializeCssArgs, hypenateProperty, isObject, withoutSpace } from '../helpers';
import { breakpointKeys, finalizeConditions, sortConditions } from './conditions';

const utilities = ""

function createCssContext() {
  const classNameByProp = new Map()
  const shorthands = new Map()
  if (utilities) {
    utilities.split(",").forEach((utility) => {
      const [prop, meta] = utility.split(":")
      const [className, ...shorthandList] = meta.split("/")
      if (className) classNameByProp.set(prop, className)
      shorthandList.forEach((shorthand) => {
        const key = shorthand === "1" ? className : shorthand
        shorthands.set(key, prop)
      })
    })
  }

  const resolveShorthand = (prop) => shorthands.get(prop) || prop

  return {
    hash: false,
    conditions: {
      shift: sortConditions,
      finalize: finalizeConditions,
      breakpoints: { keys: breakpointKeys },
    },
    utility: {
      prefix: null,
      hasShorthand: false,
      toHash(path, hashFn) {
        return hashFn(path.join(":"))
      },
      transform(prop, value) {
        const key = resolveShorthand(prop)
        const propKey = classNameByProp.get(key) || hypenateProperty(key)
        return { className: `${propKey}_${withoutSpace(value)}` }
      },
      resolveShorthand,
    },
  }
}

const cssContext = /* @__PURE__ */ createCssContext()
const serializeCss = /* @__PURE__ */ createSerializeCss(cssContext)
export const mergeCss = /* @__PURE__ */ createMergeCss(cssContext)
const serializeCssArgs = /* @__PURE__ */ createSerializeCssArgs(serializeCss, mergeCss)

export const css = /* @__PURE__ */ Object.assign(
  function css(...styles) {
    if (styles.length === 1 && isObject(styles[0])) return serializeCss(styles[0])
    return serializeCssArgs(...styles)
  },
  {
    raw: function cssRaw(...styles) {
      return mergeCss(...styles)
    },
  },
)

export const assignCss = /* @__PURE__ */ createAssignCss(cssContext)