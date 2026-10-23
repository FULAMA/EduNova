export type ColorToken = "brand.primary" | "brand.primaryHover" | "brand.primarySoft" | "colorPalette.bg" | "colorPalette.border" | "colorPalette.card" | "colorPalette.danger" | "colorPalette.info" | "colorPalette.main" | "colorPalette.muted" | "colorPalette.primary" | "colorPalette.primaryHover" | "colorPalette.primarySoft" | "colorPalette.subtle" | "colorPalette.success" | "colorPalette.warning" | "status.danger" | "status.info" | "status.success" | "status.warning" | "surface.bg" | "surface.border" | "surface.card" | "surface.subtle" | "text.main" | "text.muted"

export type FontSizeToken = "2xl" | "3xl" | "lg" | "md" | "sm" | "xl" | "xs"

export type RadiusToken = "lg" | "md" | "sm"

export type ShadowToken = "md" | "sm"

export type SpacingToken = "-1" | "-10" | "-12" | "-2" | "-3" | "-4" | "-5" | "-6" | "-7" | "-8" | "1" | "10" | "12" | "2" | "3" | "4" | "5" | "6" | "7" | "8"

export interface Tokens {
  colors: ColorToken
  fontSizes: FontSizeToken
  radii: RadiusToken
  shadows: ShadowToken
  spacing: SpacingToken
}

export type Token = `colors.${ColorToken}` | `fontSizes.${FontSizeToken}` | `radii.${RadiusToken}` | `shadows.${ShadowToken}` | `spacing.${SpacingToken}`

export type ColorOpacityModifier = `${number}`

export type ColorOpacityToken = `colors.${ColorToken}/${ColorOpacityModifier}`

export type TokenPath = Token | ColorOpacityToken

export type ColorPalette = "brand" | "status" | "surface" | "text"

export type TokenValue<T extends string> = T extends keyof Tokens ? Tokens[T] : never