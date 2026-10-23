import { colorMix, toCssVar } from '../helpers';

const tokens = {"colors.brand.primary":"#123B4A","colors.brand.primaryHover":"#0E303C","colors.brand.primarySoft":"#E8F0F2","colors.colorPalette.bg":"","colors.colorPalette.border":"","colors.colorPalette.card":"","colors.colorPalette.danger":"","colors.colorPalette.info":"","colors.colorPalette.main":"","colors.colorPalette.muted":"","colors.colorPalette.primary":"","colors.colorPalette.primaryHover":"","colors.colorPalette.primarySoft":"","colors.colorPalette.subtle":"","colors.colorPalette.success":"","colors.colorPalette.warning":"","colors.status.danger":"#B42318","colors.status.info":"#276678","colors.status.success":"#247A52","colors.status.warning":"#A66A00","colors.surface.bg":"#F7F8FA","colors.surface.border":"#D9DEE3","colors.surface.card":"#FFFFFF","colors.surface.subtle":"#F1F3F5","colors.text.main":"#182126","colors.text.muted":"#66737A","fontSizes.2xl":"22px","fontSizes.3xl":"28px","fontSizes.lg":"16px","fontSizes.md":"14px","fontSizes.sm":"13px","fontSizes.xl":"18px","fontSizes.xs":"12px","radii.lg":"8px","radii.md":"6px","radii.sm":"4px","shadows.md":"0 4px 12px rgba(24, 33, 38, 0.08)","shadows.sm":"0 1px 2px rgba(24, 33, 38, 0.06)","spacing.-1":"calc(var(--spacing-1) * -1)","spacing.-10":"calc(var(--spacing-10) * -1)","spacing.-12":"calc(var(--spacing-12) * -1)","spacing.-2":"calc(var(--spacing-2) * -1)","spacing.-3":"calc(var(--spacing-3) * -1)","spacing.-4":"calc(var(--spacing-4) * -1)","spacing.-5":"calc(var(--spacing-5) * -1)","spacing.-6":"calc(var(--spacing-6) * -1)","spacing.-7":"calc(var(--spacing-7) * -1)","spacing.-8":"calc(var(--spacing-8) * -1)","spacing.1":"4px","spacing.10":"40px","spacing.12":"48px","spacing.2":"8px","spacing.3":"12px","spacing.4":"16px","spacing.5":"20px","spacing.6":"24px","spacing.7":"28px","spacing.8":"32px"}

const tokenVars = {"spacing.-1":"var(--spacing-1)","spacing.-10":"var(--spacing-10)","spacing.-12":"var(--spacing-12)","spacing.-2":"var(--spacing-2)","spacing.-3":"var(--spacing-3)","spacing.-4":"var(--spacing-4)","spacing.-5":"var(--spacing-5)","spacing.-6":"var(--spacing-6)","spacing.-7":"var(--spacing-7)","spacing.-8":"var(--spacing-8)"}
const resolveVar = (path) => tokenVars[path] || toCssVar(path)

export const token = /* @__PURE__ */ Object.assign(
  function token(path, fallback) {
    const value = tokens[path]
    return value === undefined ? colorMix(tokens, path, resolveVar) || fallback : value || resolveVar(path)
  },
  {
    var: function tokenVar(path, fallback) {
      return tokens[path] === undefined ? fallback : resolveVar(path)
    },
  },
)