export type Pretty<T> = { [K in keyof T]: T[K] } & {}

export type DistributiveOmit<T, K extends keyof any> = T extends unknown ? Omit<T, K> : never

export type DistributiveUnion<T, U> = {
  [K in keyof T]: K extends keyof U ? U[K] | T[K] : T[K]
} & DistributiveOmit<U, keyof T>

export type Assign<T, U> = {
  [K in keyof T]: K extends keyof U ? U[K] : T[K]
} & U

export interface Conditions {
  "base": string
}

export interface Breakpoints {
  "base": string
}

export type ContainerName = AnyString
export type CssContainer = ContainerName | `${ContainerName} / inline-size` | `${ContainerName} / size` | AnyString

export type Condition = keyof Conditions

export type ConditionalValue<T> =
  | T
  | Array<T | null | undefined>
  | { [K in Condition]?: ConditionalValue<T> }
  | undefined

export type AnyString = string & {}

export type AnyNumber = number & {}

export type CssVars = `var(--${string})`

export type WithEscapeHatch<T> = T | `[${string}]`

export type OnlyKnown<Value> = Value extends boolean ? Value : Value extends `${infer _}` ? Value : never

export type ColorPaletteValue = "brand" | "status" | "surface" | "text" | CssVars | AnyString | AnyNumber

export type AtRuleType = "media" | "layer" | "container" | "supports" | "page" | "scope" | "starting-style"

export type Selector = `${string}&` | `&${string}` | `@${AtRuleType}${string}`

export type AnySelector = Selector | string

export type CssGlobals = "inherit" | "initial" | "revert" | "revert-layer" | "unset"

export type CssColorGlobals = CssGlobals | "currentColor" | "transparent"

export type CssDimensionGlobals = CssGlobals | "auto" | "fit-content" | "max-content" | "min-content"

export type CssAutoGlobals = CssGlobals | "auto"

export type CssLength = CssDimensionGlobals | (string & {}) | number

export type CssNamedColor = "aliceblue" | "antiquewhite" | "aqua" | "aquamarine" | "azure" | "beige" | "bisque" | "black" | "blanchedalmond" | "blue" | "blueviolet" | "brown" | "burlywood" | "cadetblue" | "chartreuse" | "chocolate" | "coral" | "cornflowerblue" | "cornsilk" | "crimson" | "cyan" | "darkblue" | "darkcyan" | "darkgoldenrod" | "darkgray" | "darkgreen" | "darkgrey" | "darkkhaki" | "darkmagenta" | "darkolivegreen" | "darkorange" | "darkorchid" | "darkred" | "darksalmon" | "darkseagreen" | "darkslateblue" | "darkslategray" | "darkslategrey" | "darkturquoise" | "darkviolet" | "deeppink" | "deepskyblue" | "dimgray" | "dimgrey" | "dodgerblue" | "firebrick" | "floralwhite" | "forestgreen" | "fuchsia" | "gainsboro" | "ghostwhite" | "gold" | "goldenrod" | "gray" | "green" | "greenyellow" | "grey" | "honeydew" | "hotpink" | "indianred" | "indigo" | "ivory" | "khaki" | "lavender" | "lavenderblush" | "lawngreen" | "lemonchiffon" | "lightblue" | "lightcoral" | "lightcyan" | "lightgoldenrodyellow" | "lightgray" | "lightgreen" | "lightgrey" | "lightpink" | "lightsalmon" | "lightseagreen" | "lightskyblue" | "lightslategray" | "lightslategrey" | "lightsteelblue" | "lightyellow" | "lime" | "limegreen" | "linen" | "magenta" | "maroon" | "mediumaquamarine" | "mediumblue" | "mediumorchid" | "mediumpurple" | "mediumseagreen" | "mediumslateblue" | "mediumspringgreen" | "mediumturquoise" | "mediumvioletred" | "midnightblue" | "mintcream" | "mistyrose" | "moccasin" | "navajowhite" | "navy" | "oldlace" | "olive" | "olivedrab" | "orange" | "orangered" | "orchid" | "palegoldenrod" | "palegreen" | "paleturquoise" | "palevioletred" | "papayawhip" | "peachpuff" | "peru" | "pink" | "plum" | "powderblue" | "purple" | "rebeccapurple" | "red" | "rosybrown" | "royalblue" | "saddlebrown" | "salmon" | "sandybrown" | "seagreen" | "seashell" | "sienna" | "silver" | "skyblue" | "slateblue" | "slategray" | "slategrey" | "snow" | "springgreen" | "steelblue" | "tan" | "teal" | "thistle" | "tomato" | "turquoise" | "violet" | "wheat" | "white" | "whitesmoke" | "yellow" | "yellowgreen"

export type CssSystemColor = "AccentColor" | "AccentColorText" | "ActiveText" | "ButtonBorder" | "ButtonFace" | "ButtonText" | "Canvas" | "CanvasText" | "Field" | "FieldText" | "GrayText" | "Highlight" | "HighlightText" | "LinkText" | "Mark" | "MarkText" | "SelectedItem" | "SelectedItemText" | "VisitedText"

export type CssColor = CssColorGlobals | CssNamedColor | CssSystemColor | (string & {})

export type CssAbsoluteSize = "large" | "medium" | "small" | "x-large" | "x-small" | "xx-large" | "xx-small" | "xxx-large"

export type CssBgSize = CssLength | "auto" | "contain" | "cover"

export type CssFontSize = CssLength | CssAbsoluteSize | "larger" | "smaller" | "math"

export type CssFontWeight = CssGlobals | "bold" | "normal" | (string & {}) | number

export type CssLineWidth = CssLength | "medium" | "thick" | "thin"

export type CssLineStyle = CssGlobals | "dashed" | "dotted" | "double" | "groove" | "hidden" | "inset" | "none" | "outset" | "ridge" | "solid"

export type CssLineStyleOpen = CssLineStyle | (string & {})

export type CssRepeatStyle = CssGlobals | "no-repeat" | "repeat" | "repeat-x" | "repeat-y" | "round" | "space" | (string & {})

export type CssFontStretch = CssGlobals | "condensed" | "expanded" | "extra-condensed" | "extra-expanded" | "normal" | "semi-condensed" | "semi-expanded" | "ultra-condensed" | "ultra-expanded" | (string & {})

export type CssOverflow = CssGlobals | "-moz-hidden-unscrollable" | "auto" | "clip" | "hidden" | "overlay" | "scroll" | "visible"

export type CssOverflowOpen = CssOverflow | (string & {})

export type CssOverflowShort = CssGlobals | "auto" | "clip" | "hidden" | "scroll" | "visible"

export type CssOverscrollBehavior = CssGlobals | "auto" | "contain" | "none"

export type CssOverscrollBehaviorOpen = CssOverscrollBehavior | (string & {})

export type CssPosition = CssLength | "bottom" | "center" | "left" | "right" | "top"

export type CssGenericFamily = "-apple-system" | "cursive" | "emoji" | "fangsong" | "fantasy" | "math" | "monospace" | "sans-serif" | "serif" | "system-ui" | "ui-monospace" | "ui-rounded" | "ui-sans-serif" | "ui-serif"

export type CssFontFamily = CssGlobals | CssGenericFamily | (string & {})

export type CssNumeric = CssGlobals | (string & {}) | number

export type CssZIndex = CssAutoGlobals | (string & {}) | number

export type CssAny = CssGlobals | (string & {}) | number

export type PropertyValueMap = {
  accentColor: CssColor
  alignContent: CssGlobals | "baseline" | "center" | "end" | "first baseline" | "flex-end" | "flex-start" | "last baseline" | "normal" | "safe center" | "safe end" | "safe start" | "space-around" | "space-between" | "space-evenly" | "start" | "stretch" | (string & {})
  alignItems: CssGlobals | "anchor-center" | "baseline" | "center" | "end" | "first baseline" | "flex-end" | "flex-start" | "last baseline" | "normal" | "safe center" | "safe end" | "safe start" | "self-end" | "self-start" | "start" | "stretch" | (string & {})
  alignSelf: CssGlobals | "anchor-center" | "auto" | "baseline" | "center" | "end" | "first baseline" | "flex-end" | "flex-start" | "last baseline" | "normal" | "safe center" | "safe end" | "safe start" | "self-end" | "self-start" | "start" | "stretch" | (string & {})
  alignmentBaseline: CssGlobals | "alphabetic" | "baseline" | "central" | "ideographic" | "mathematical" | "middle" | "text-after-edge" | "text-before-edge"
  appearance: CssGlobals | "auto" | "button" | "checkbox" | "listbox" | "menulist" | "menulist-button" | "meter" | "none" | "progress-bar" | "radio" | "searchfield" | "textarea" | "textfield"
  backgroundColor: CssColor
  backgroundPosition: CssPosition
  backgroundRepeat: CssRepeatStyle
  backgroundSize: CssBgSize
  baselineShift: CssLength
  blockSize: CssLength
  borderBlockColor: CssColor
  borderBlockEndColor: CssColor
  borderBlockEndStyle: CssLineStyle
  borderBlockEndWidth: CssLineWidth
  borderBlockStartColor: CssColor
  borderBlockStartStyle: CssLineStyle
  borderBlockStartWidth: CssLineWidth
  borderBlockStyle: CssLineStyleOpen
  borderBlockWidth: CssLineWidth
  borderBottomColor: CssColor
  borderBottomLeftRadius: CssLength
  borderBottomRightRadius: CssLength
  borderBottomStyle: CssLineStyle
  borderBottomWidth: CssLineWidth
  borderColor: CssColor
  borderEndEndRadius: CssLength
  borderEndStartRadius: CssLength
  borderImage: CssGlobals | "none" | "repeat" | "round" | "space" | "stretch" | (string & {})
  borderImageWidth: CssLength
  borderInlineColor: CssColor
  borderInlineEndColor: CssColor
  borderInlineEndStyle: CssLineStyle
  borderInlineEndWidth: CssLineWidth
  borderInlineStartColor: CssColor
  borderInlineStartStyle: CssLineStyle
  borderInlineStartWidth: CssLineWidth
  borderInlineStyle: CssLineStyleOpen
  borderInlineWidth: CssLineWidth
  borderLeftColor: CssColor
  borderLeftStyle: CssLineStyle
  borderLeftWidth: CssLineWidth
  borderRadius: CssLength
  borderRightColor: CssColor
  borderRightStyle: CssLineStyle
  borderRightWidth: CssLineWidth
  borderSpacing: CssLength
  borderStartEndRadius: CssLength
  borderStartStartRadius: CssLength
  borderStyle: CssLineStyleOpen
  borderTopColor: CssColor
  borderTopLeftRadius: CssLength
  borderTopRightRadius: CssLength
  borderTopStyle: CssLineStyle
  borderTopWidth: CssLineWidth
  borderWidth: CssLineWidth
  bottom: CssLength
  boxAlign: CssGlobals | "baseline" | "center" | "end" | "start" | "stretch"
  breakAfter: CssGlobals | "all" | "always" | "auto" | "avoid" | "avoid-column" | "avoid-page" | "avoid-region" | "column" | "left" | "page" | "recto" | "region" | "right" | "verso"
  breakBefore: PropertyValueMap["breakAfter"]
  breakInside: CssGlobals | "auto" | "avoid" | "avoid-column" | "avoid-page" | "avoid-region"
  caret: CssGlobals | "auto" | "bar" | "block" | "currentColor" | "underscore" | (string & {})
  caretColor: CssColor
  clear: CssGlobals | "both" | "inline-end" | "inline-start" | "left" | "none" | "right"
  clipPath: CssGlobals | "fill-box" | "margin-box" | "none" | "stroke-box" | "view-box" | (string & {})
  color: CssColor
  colorScheme: CssGlobals | "dark" | "light" | "normal" | (string & {})
  columnGap: CssLength
  columnRuleColor: CssColor
  columnRuleStyle: CssLineStyleOpen
  columnRuleWidth: CssLineWidth
  columnWidth: CssLength
  contain: CssGlobals | "content" | "inline-size" | "layout" | "none" | "paint" | "size" | "strict" | "style" | (string & {})
  containIntrinsicBlockSize: CssLength
  containIntrinsicHeight: CssLength
  containIntrinsicInlineSize: CssLength
  containIntrinsicSize: CssLength
  containIntrinsicWidth: CssLength
  containerType: CssGlobals | "inline-size" | "normal" | "scroll-state" | "size" | (string & {})
  content: CssGlobals | "close-quote" | "no-close-quote" | "no-open-quote" | "none" | "normal" | "open-quote" | (string & {})
  cursor: CssGlobals | "-moz-grab" | "-moz-zoom-in" | "-moz-zoom-out" | "-webkit-grab" | "-webkit-grabbing" | "-webkit-zoom-in" | "-webkit-zoom-out" | "alias" | "all-scroll" | "auto" | "cell" | "col-resize" | "context-menu" | "copy" | "crosshair" | "default" | "e-resize" | "ew-resize" | "grab" | "grabbing" | "help" | "move" | "n-resize" | "ne-resize" | "nesw-resize" | "no-drop" | "none" | "not-allowed" | "ns-resize" | "nw-resize" | "nwse-resize" | "pointer" | "progress" | "row-resize" | "s-resize" | "se-resize" | "sw-resize" | "text" | "vertical-text" | "w-resize" | "wait" | "zoom-in" | "zoom-out" | (string & {})
  display: CssGlobals | "-ms-flexbox" | "-ms-grid" | "-ms-inline-flexbox" | "-ms-inline-grid" | "-webkit-flex" | "-webkit-inline-flex" | "block" | "contents" | "flex" | "flow" | "flow-root" | "grid" | "inline" | "inline-block" | "inline-flex" | "inline-grid" | "inline-list-item" | "inline-table" | "list-item" | "none" | "ruby" | "ruby-base" | "ruby-base-container" | "ruby-text" | "ruby-text-container" | "run-in" | "table" | "table-caption" | "table-cell" | "table-column" | "table-column-group" | "table-footer-group" | "table-header-group" | "table-row" | "table-row-group" | (string & {})
  dominantBaseline: CssGlobals | "alphabetic" | "auto" | "central" | "hanging" | "ideographic" | "mathematical" | "middle" | "text-bottom" | "text-top"
  fieldSizing: CssGlobals | "content" | "fixed"
  flexBasis: CssLength
  flexFlow: CssGlobals | "column" | "column-reverse" | "nowrap" | "row" | "row-reverse" | "wrap" | "wrap-reverse" | (string & {})
  flexGrow: CssNumeric
  flexShrink: CssNumeric
  float: CssGlobals | "inline-end" | "inline-start" | "left" | "none" | "right"
  floodColor: CssColor
  font: CssGlobals | "caption" | "icon" | "menu" | "message-box" | "small-caption" | "status-bar" | (string & {})
  fontFamily: CssFontFamily
  fontSize: CssFontSize
  fontSizeAdjust: CssLength
  fontStretch: CssFontStretch
  fontStyle: CssGlobals | "italic" | "normal" | "oblique" | (string & {})
  fontSynthesis: CssGlobals | "none" | "position" | "small-caps" | "style" | "weight" | (string & {})
  fontVariantCaps: CssGlobals | "all-petite-caps" | "all-small-caps" | "normal" | "petite-caps" | "small-caps" | "titling-caps" | "unicase"
  fontVariantEastAsian: CssGlobals | "full-width" | "jis04" | "jis78" | "jis83" | "jis90" | "normal" | "proportional-width" | "ruby" | "simplified" | "traditional" | (string & {})
  fontVariantLigatures: CssGlobals | "common-ligatures" | "contextual" | "discretionary-ligatures" | "historical-ligatures" | "no-common-ligatures" | "no-contextual" | "no-discretionary-ligatures" | "no-historical-ligatures" | "none" | "normal" | (string & {})
  fontVariantNumeric: CssGlobals | "diagonal-fractions" | "lining-nums" | "normal" | "oldstyle-nums" | "ordinal" | "proportional-nums" | "slashed-zero" | "stacked-fractions" | "tabular-nums" | (string & {})
  fontWeight: CssFontWeight
  fontWidth: CssFontStretch
  gap: CssLength
  gridAutoFlow: CssGlobals | "column" | "dense" | "row" | (string & {})
  gridColumnGap: CssLength
  gridGap: CssLength
  gridRowGap: CssLength
  hangingPunctuation: CssGlobals | "allow-end" | "first" | "force-end" | "last" | "none" | (string & {})
  height: CssLength
  hyphens: CssGlobals | "auto" | "manual" | "none"
  imageRendering: CssGlobals | "-moz-crisp-edges" | "-webkit-optimize-contrast" | "auto" | "crisp-edges" | "pixelated" | "smooth"
  imeMode: CssGlobals | "active" | "auto" | "disabled" | "inactive" | "normal"
  inlineSize: CssLength
  inset: CssLength
  justifyContent: CssGlobals | "center" | "end" | "flex-end" | "flex-start" | "left" | "normal" | "right" | "safe center" | "safe end" | "safe start" | "space-around" | "space-between" | "space-evenly" | "start" | "stretch" | (string & {})
  justifyItems: CssGlobals | "anchor-center" | "baseline" | "center" | "end" | "first baseline" | "flex-end" | "flex-start" | "last baseline" | "left" | "legacy" | "normal" | "right" | "safe center" | "safe end" | "safe start" | "self-end" | "self-start" | "start" | "stretch" | (string & {})
  justifySelf: CssGlobals | "anchor-center" | "auto" | "baseline" | "center" | "end" | "first baseline" | "flex-end" | "flex-start" | "last baseline" | "left" | "normal" | "right" | "safe center" | "safe end" | "safe start" | "self-end" | "self-start" | "start" | "stretch" | (string & {})
  left: CssLength
  letterSpacing: CssLength
  lightingColor: CssColor
  lineBreak: CssGlobals | "anywhere" | "auto" | "loose" | "normal" | "strict"
  lineHeight: CssNumeric
  lineHeightStep: CssLength
  listStyleImage: CssGlobals | "none" | (string & {})
  listStylePosition: CssGlobals | "inside" | "outside"
  listStyleType: PropertyValueMap["listStyleImage"]
  margin: CssLength
  marginBottom: CssLength
  marginLeft: CssLength
  marginRight: CssLength
  marginTop: CssLength
  maskBorder: CssGlobals | "alpha" | "luminance" | "none" | "repeat" | "round" | "space" | "stretch" | (string & {})
  maskBorderWidth: CssLength
  maskPosition: CssPosition
  maskRepeat: CssRepeatStyle
  maskSize: CssBgSize
  maxBlockSize: CssLength
  maxHeight: CssLength
  maxInlineSize: CssLength
  maxWidth: CssLength
  minBlockSize: CssLength
  minHeight: CssLength
  minInlineSize: CssLength
  minWidth: CssLength
  mixBlendMode: CssGlobals | "color" | "color-burn" | "color-dodge" | "darken" | "difference" | "exclusion" | "hard-light" | "hue" | "lighten" | "luminosity" | "multiply" | "normal" | "overlay" | "plus-darker" | "plus-lighter" | "saturation" | "screen" | "soft-light"
  objectFit: CssGlobals | "contain" | "cover" | "fill" | "none" | "scale-down"
  objectPosition: CssPosition
  offsetAnchor: CssPosition
  offsetPosition: CssPosition
  opacity: CssNumeric
  order: CssNumeric
  orphans: CssNumeric
  outlineColor: CssColor
  outlineOffset: CssLength
  outlineStyle: CssGlobals | "auto" | "dashed" | "dotted" | "double" | "groove" | "inset" | "none" | "outset" | "ridge" | "solid"
  outlineWidth: CssLineWidth
  overflow: CssOverflowOpen
  overflowBlock: CssOverflowShort
  overflowClipMargin: CssLength
  overflowInline: CssOverflowShort
  overflowX: CssOverflow
  overflowY: CssOverflow
  overscrollBehavior: CssOverscrollBehaviorOpen
  overscrollBehaviorX: CssOverscrollBehavior
  overscrollBehaviorY: CssOverscrollBehavior
  padding: CssLength
  paddingBottom: CssLength
  paddingLeft: CssLength
  paddingRight: CssLength
  paddingTop: CssLength
  pageBreakAfter: CssGlobals | "always" | "auto" | "avoid" | "left" | "recto" | "right" | "verso"
  pageBreakBefore: PropertyValueMap["pageBreakAfter"]
  perspective: CssLength
  perspectiveOrigin: CssPosition
  placeContent: PropertyValueMap["alignContent"]
  placeItems: PropertyValueMap["alignItems"]
  placeSelf: PropertyValueMap["alignSelf"]
  pointerEvents: CssGlobals | "all" | "auto" | "fill" | "none" | "painted" | "stroke" | "visible" | "visibleFill" | "visiblePainted" | "visibleStroke"
  position: CssGlobals | "-webkit-sticky" | "absolute" | "fixed" | "relative" | "static" | "sticky"
  positionTryOrder: CssGlobals | "most-block-size" | "most-height" | "most-inline-size" | "most-width" | "normal"
  resize: CssGlobals | "block" | "both" | "horizontal" | "inline" | "none" | "vertical"
  right: CssLength
  rowGap: CssLength
  scrollMarginBlock: CssLength
  scrollMarginBlockEnd: CssLength
  scrollMarginBlockStart: CssLength
  scrollMarginBottom: CssLength
  scrollMarginInline: CssLength
  scrollMarginInlineEnd: CssLength
  scrollMarginInlineStart: CssLength
  scrollMarginLeft: CssLength
  scrollMarginRight: CssLength
  scrollMarginTop: CssLength
  scrollPaddingBlock: CssLength
  scrollPaddingBlockEnd: CssLength
  scrollPaddingBlockStart: CssLength
  scrollPaddingBottom: CssLength
  scrollPaddingInline: CssLength
  scrollPaddingInlineEnd: CssLength
  scrollPaddingInlineStart: CssLength
  scrollPaddingLeft: CssLength
  scrollPaddingRight: CssLength
  scrollPaddingTop: CssLength
  scrollSnapAlign: CssGlobals | "center" | "end" | "none" | "start" | (string & {})
  scrollSnapDestination: CssPosition
  scrollSnapStop: CssGlobals | "always" | "normal"
  scrollSnapType: CssGlobals | "block" | "both" | "inline" | "none" | "x" | "y" | (string & {})
  scrollbarGutter: CssGlobals | "auto" | "stable" | "stable both-edges" | (string & {})
  scrollbarWidth: CssGlobals | "auto" | "none" | "thin"
  shapeMargin: CssLength
  shapeOutside: CssGlobals | "border-box" | "content-box" | "margin-box" | "none" | "padding-box" | (string & {})
  speakAs: CssGlobals | "digits" | "literal-punctuation" | "no-punctuation" | "normal" | "spell-out" | (string & {})
  stopColor: CssColor
  strokeColor: CssColor
  strokeLinejoin: CssGlobals | "arcs" | "bevel" | "miter" | "miter-clip" | "round"
  strokeWidth: CssLength
  tabSize: CssLength
  tableLayout: CssGlobals | "auto" | "fixed"
  textAlign: CssGlobals | "-khtml-center" | "-khtml-left" | "-khtml-right" | "-moz-center" | "-moz-left" | "-moz-right" | "-webkit-center" | "-webkit-left" | "-webkit-match-parent" | "-webkit-right" | "center" | "end" | "justify" | "left" | "match-parent" | "right" | "start"
  textAlignLast: CssGlobals | "auto" | "center" | "end" | "justify" | "left" | "right" | "start"
  textAutospace: CssGlobals | "auto" | "ideograph-alpha" | "ideograph-numeric" | "insert" | "no-autospace" | "normal" | "punctuation" | "replace" | (string & {})
  textBox: CssGlobals | "auto" | "cap" | "ex" | "ideographic" | "ideographic-ink" | "none" | "normal" | "text" | "trim-both" | "trim-end" | "trim-start" | (string & {})
  textBoxEdge: CssGlobals | "auto" | "cap" | "ex" | "ideographic" | "ideographic-ink" | "text" | (string & {})
  textDecorationColor: CssColor
  textDecorationLine: CssGlobals | "blink" | "grammar-error" | "line-through" | "none" | "overline" | "spelling-error" | "underline" | (string & {})
  textDecorationSkip: CssGlobals | "box-decoration" | "edges" | "leading-spaces" | "none" | "objects" | "spaces" | "trailing-spaces" | (string & {})
  textDecorationSkipInk: CssGlobals | "all" | "auto" | "none"
  textDecorationStyle: CssGlobals | "dashed" | "dotted" | "double" | "solid" | "wavy"
  textDecorationThickness: CssLength
  textEmphasis: CssGlobals | "circle" | "currentColor" | "dot" | "double-circle" | "filled" | "none" | "open" | "sesame" | "triangle" | (string & {})
  textEmphasisColor: CssColor
  textEmphasisPosition: CssGlobals | "auto" | "over" | "under" | (string & {})
  textEmphasisStyle: CssGlobals | "circle" | "dot" | "double-circle" | "filled" | "none" | "open" | "sesame" | "triangle" | (string & {})
  textIndent: CssLength
  textJustify: CssGlobals | "auto" | "distribute" | "inter-character" | "inter-word" | "none"
  textOrientation: CssGlobals | "mixed" | "sideways" | "sideways-right" | "upright"
  textOverflow: CssGlobals | "clip" | "ellipsis" | (string & {})
  textRendering: CssGlobals | "auto" | "geometricPrecision" | "optimizeLegibility" | "optimizeSpeed"
  textSizeAdjust: CssLength
  textTransform: CssGlobals | "capitalize" | "full-size-kana" | "full-width" | "lowercase" | "math-auto" | "none" | "uppercase" | (string & {})
  textUnderlineOffset: CssLength
  textUnderlinePosition: CssGlobals | "auto" | "from-font" | "left" | "right" | "under" | (string & {})
  textWrap: CssGlobals | "auto" | "balance" | "nowrap" | "pretty" | "stable" | "wrap" | (string & {})
  textWrapMode: CssGlobals | "nowrap" | "wrap"
  textWrapStyle: CssGlobals | "auto" | "balance" | "pretty" | "stable"
  top: CssLength
  touchAction: CssGlobals | "-ms-manipulation" | "-ms-none" | "-ms-pan-x" | "-ms-pan-y" | "-ms-pinch-zoom" | "auto" | "manipulation" | "none" | "pan-down" | "pan-left" | "pan-right" | "pan-up" | "pan-x" | "pan-y" | "pinch-zoom" | (string & {})
  transformBox: CssGlobals | "border-box" | "content-box" | "fill-box" | "stroke-box" | "view-box"
  transitionBehavior: CssGlobals | "allow-discrete" | "normal" | (string & {})
  transitionProperty: CssGlobals | "all" | "none" | (string & {})
  unicodeBidi: CssGlobals | "-moz-isolate" | "-moz-isolate-override" | "-moz-plaintext" | "-webkit-isolate" | "-webkit-isolate-override" | "-webkit-plaintext" | "bidi-override" | "embed" | "isolate" | "isolate-override" | "normal" | "plaintext"
  userSelect: CssGlobals | "-moz-none" | "all" | "auto" | "none" | "text"
  vectorEffect: CssGlobals | "fixed-position" | "non-rotation" | "non-scaling-size" | "non-scaling-stroke" | "none"
  verticalAlign: CssGlobals | "baseline" | "bottom" | "middle" | "sub" | "super" | "text-bottom" | "text-top" | "top" | (string & {})
  viewTimelineInset: CssLength
  whiteSpace: CssGlobals | "-moz-pre-wrap" | "break-spaces" | "collapse" | "normal" | "nowrap" | "pre" | "pre-line" | "pre-wrap" | "preserve" | "preserve-breaks" | "preserve-spaces" | "wrap" | (string & {})
  whiteSpaceCollapse: CssGlobals | "break-spaces" | "collapse" | "preserve" | "preserve-breaks" | "preserve-spaces"
  widows: CssNumeric
  width: CssLength
  wordBreak: CssGlobals | "auto-phrase" | "break-all" | "break-word" | "keep-all" | "normal"
  wordSpacing: CssLength
  wordWrap: CssGlobals | "break-word" | "normal"
  writingMode: CssGlobals | "horizontal-tb" | "sideways-lr" | "sideways-rl" | "vertical-lr" | "vertical-rl"
  zIndex: CssZIndex
  zoom: CssNumeric
}

export interface SystemProperties {
  WebkitAppearance?: ConditionalValue<CssAny>
  WebkitBorderBefore?: ConditionalValue<CssAny>
  WebkitBorderBeforeColor?: ConditionalValue<CssAny>
  WebkitBorderBeforeStyle?: ConditionalValue<CssAny>
  WebkitBorderBeforeWidth?: ConditionalValue<CssAny>
  WebkitBoxReflect?: ConditionalValue<CssAny>
  WebkitLineClamp?: ConditionalValue<CssAny>
  WebkitMask?: ConditionalValue<CssAny>
  WebkitMaskAttachment?: ConditionalValue<CssAny>
  WebkitMaskClip?: ConditionalValue<CssAny>
  WebkitMaskComposite?: ConditionalValue<CssAny>
  WebkitMaskImage?: ConditionalValue<CssAny>
  WebkitMaskOrigin?: ConditionalValue<CssAny>
  WebkitMaskPosition?: ConditionalValue<CssAny>
  WebkitMaskPositionX?: ConditionalValue<CssAny>
  WebkitMaskPositionY?: ConditionalValue<CssAny>
  WebkitMaskRepeat?: ConditionalValue<CssAny>
  WebkitMaskRepeatX?: ConditionalValue<CssAny>
  WebkitMaskRepeatY?: ConditionalValue<CssAny>
  WebkitMaskSize?: ConditionalValue<CssAny>
  WebkitOverflowScrolling?: ConditionalValue<CssAny>
  WebkitTapHighlightColor?: ConditionalValue<CssAny>
  WebkitTextFillColor?: ConditionalValue<CssAny>
  WebkitTextStroke?: ConditionalValue<CssAny>
  WebkitTextStrokeColor?: ConditionalValue<CssAny>
  WebkitTextStrokeWidth?: ConditionalValue<CssAny>
  WebkitTouchCallout?: ConditionalValue<CssAny>
  WebkitUserModify?: ConditionalValue<CssAny>
  WebkitUserSelect?: ConditionalValue<CssAny>
  accentColor?: ConditionalValue<PropertyValueMap["accentColor"]>
  alignContent?: ConditionalValue<PropertyValueMap["alignContent"]>
  alignItems?: ConditionalValue<PropertyValueMap["alignItems"]>
  alignSelf?: ConditionalValue<PropertyValueMap["alignSelf"]>
  alignTracks?: ConditionalValue<CssAny>
  alignmentBaseline?: ConditionalValue<PropertyValueMap["alignmentBaseline"] | AnyString>
  all?: ConditionalValue<CssAny>
  anchorName?: ConditionalValue<CssAny>
  anchorScope?: ConditionalValue<CssAny>
  animation?: ConditionalValue<CssAny>
  animationComposition?: ConditionalValue<CssAny>
  animationDelay?: ConditionalValue<CssAny>
  animationDirection?: ConditionalValue<CssAny>
  animationDuration?: ConditionalValue<CssAny>
  animationFillMode?: ConditionalValue<CssAny>
  animationIterationCount?: ConditionalValue<CssAny>
  animationName?: ConditionalValue<CssAny>
  animationPlayState?: ConditionalValue<CssAny>
  animationRange?: ConditionalValue<CssAny>
  animationRangeEnd?: ConditionalValue<CssAny>
  animationRangeStart?: ConditionalValue<CssAny>
  animationTimeline?: ConditionalValue<CssAny>
  animationTimingFunction?: ConditionalValue<CssAny>
  appearance?: ConditionalValue<PropertyValueMap["appearance"] | AnyString>
  aspectRatio?: ConditionalValue<CssAny>
  backdropFilter?: ConditionalValue<CssAny>
  backfaceVisibility?: ConditionalValue<CssAny>
  background?: ConditionalValue<CssAny>
  backgroundAttachment?: ConditionalValue<CssAny>
  backgroundBlendMode?: ConditionalValue<CssAny>
  backgroundClip?: ConditionalValue<CssAny>
  backgroundColor?: ConditionalValue<PropertyValueMap["backgroundColor"]>
  backgroundImage?: ConditionalValue<CssAny>
  backgroundOrigin?: ConditionalValue<CssAny>
  backgroundPosition?: ConditionalValue<PropertyValueMap["backgroundPosition"]>
  backgroundPositionX?: ConditionalValue<CssAny>
  backgroundPositionY?: ConditionalValue<CssAny>
  backgroundRepeat?: ConditionalValue<PropertyValueMap["backgroundRepeat"]>
  backgroundSize?: ConditionalValue<PropertyValueMap["backgroundSize"]>
  baselineShift?: ConditionalValue<PropertyValueMap["baselineShift"]>
  blockSize?: ConditionalValue<PropertyValueMap["blockSize"]>
  border?: ConditionalValue<CssAny>
  borderBlock?: ConditionalValue<CssAny>
  borderBlockColor?: ConditionalValue<PropertyValueMap["borderBlockColor"]>
  borderBlockEnd?: ConditionalValue<CssAny>
  borderBlockEndColor?: ConditionalValue<PropertyValueMap["borderBlockEndColor"]>
  borderBlockEndStyle?: ConditionalValue<PropertyValueMap["borderBlockEndStyle"] | AnyString>
  borderBlockEndWidth?: ConditionalValue<PropertyValueMap["borderBlockEndWidth"]>
  borderBlockStart?: ConditionalValue<CssAny>
  borderBlockStartColor?: ConditionalValue<PropertyValueMap["borderBlockStartColor"]>
  borderBlockStartStyle?: ConditionalValue<PropertyValueMap["borderBlockStartStyle"] | AnyString>
  borderBlockStartWidth?: ConditionalValue<PropertyValueMap["borderBlockStartWidth"]>
  borderBlockStyle?: ConditionalValue<PropertyValueMap["borderBlockStyle"]>
  borderBlockWidth?: ConditionalValue<PropertyValueMap["borderBlockWidth"]>
  borderBottom?: ConditionalValue<CssAny>
  borderBottomColor?: ConditionalValue<PropertyValueMap["borderBottomColor"]>
  borderBottomLeftRadius?: ConditionalValue<PropertyValueMap["borderBottomLeftRadius"]>
  borderBottomRightRadius?: ConditionalValue<PropertyValueMap["borderBottomRightRadius"]>
  borderBottomStyle?: ConditionalValue<PropertyValueMap["borderBottomStyle"] | AnyString>
  borderBottomWidth?: ConditionalValue<PropertyValueMap["borderBottomWidth"]>
  borderCollapse?: ConditionalValue<CssAny>
  borderColor?: ConditionalValue<PropertyValueMap["borderColor"]>
  borderEndEndRadius?: ConditionalValue<PropertyValueMap["borderEndEndRadius"]>
  borderEndStartRadius?: ConditionalValue<PropertyValueMap["borderEndStartRadius"]>
  borderImage?: ConditionalValue<PropertyValueMap["borderImage"]>
  borderImageOutset?: ConditionalValue<CssAny>
  borderImageRepeat?: ConditionalValue<CssAny>
  borderImageSlice?: ConditionalValue<CssAny>
  borderImageSource?: ConditionalValue<CssAny>
  borderImageWidth?: ConditionalValue<PropertyValueMap["borderImageWidth"]>
  borderInline?: ConditionalValue<CssAny>
  borderInlineColor?: ConditionalValue<PropertyValueMap["borderInlineColor"]>
  borderInlineEnd?: ConditionalValue<CssAny>
  borderInlineEndColor?: ConditionalValue<PropertyValueMap["borderInlineEndColor"]>
  borderInlineEndStyle?: ConditionalValue<PropertyValueMap["borderInlineEndStyle"] | AnyString>
  borderInlineEndWidth?: ConditionalValue<PropertyValueMap["borderInlineEndWidth"]>
  borderInlineStart?: ConditionalValue<CssAny>
  borderInlineStartColor?: ConditionalValue<PropertyValueMap["borderInlineStartColor"]>
  borderInlineStartStyle?: ConditionalValue<PropertyValueMap["borderInlineStartStyle"] | AnyString>
  borderInlineStartWidth?: ConditionalValue<PropertyValueMap["borderInlineStartWidth"]>
  borderInlineStyle?: ConditionalValue<PropertyValueMap["borderInlineStyle"]>
  borderInlineWidth?: ConditionalValue<PropertyValueMap["borderInlineWidth"]>
  borderLeft?: ConditionalValue<CssAny>
  borderLeftColor?: ConditionalValue<PropertyValueMap["borderLeftColor"]>
  borderLeftStyle?: ConditionalValue<PropertyValueMap["borderLeftStyle"] | AnyString>
  borderLeftWidth?: ConditionalValue<PropertyValueMap["borderLeftWidth"]>
  borderRadius?: ConditionalValue<PropertyValueMap["borderRadius"]>
  borderRight?: ConditionalValue<CssAny>
  borderRightColor?: ConditionalValue<PropertyValueMap["borderRightColor"]>
  borderRightStyle?: ConditionalValue<PropertyValueMap["borderRightStyle"] | AnyString>
  borderRightWidth?: ConditionalValue<PropertyValueMap["borderRightWidth"]>
  borderSpacing?: ConditionalValue<PropertyValueMap["borderSpacing"]>
  borderStartEndRadius?: ConditionalValue<PropertyValueMap["borderStartEndRadius"]>
  borderStartStartRadius?: ConditionalValue<PropertyValueMap["borderStartStartRadius"]>
  borderStyle?: ConditionalValue<PropertyValueMap["borderStyle"]>
  borderTop?: ConditionalValue<CssAny>
  borderTopColor?: ConditionalValue<PropertyValueMap["borderTopColor"]>
  borderTopLeftRadius?: ConditionalValue<PropertyValueMap["borderTopLeftRadius"]>
  borderTopRightRadius?: ConditionalValue<PropertyValueMap["borderTopRightRadius"]>
  borderTopStyle?: ConditionalValue<PropertyValueMap["borderTopStyle"] | AnyString>
  borderTopWidth?: ConditionalValue<PropertyValueMap["borderTopWidth"]>
  borderWidth?: ConditionalValue<PropertyValueMap["borderWidth"]>
  bottom?: ConditionalValue<PropertyValueMap["bottom"]>
  boxAlign?: ConditionalValue<PropertyValueMap["boxAlign"] | AnyString>
  boxDecorationBreak?: ConditionalValue<CssAny>
  boxDirection?: ConditionalValue<CssAny>
  boxFlex?: ConditionalValue<CssAny>
  boxFlexGroup?: ConditionalValue<CssAny>
  boxLines?: ConditionalValue<CssAny>
  boxOrdinalGroup?: ConditionalValue<CssAny>
  boxOrient?: ConditionalValue<CssAny>
  boxPack?: ConditionalValue<CssAny>
  boxShadow?: ConditionalValue<CssAny>
  boxSizing?: ConditionalValue<CssAny>
  breakAfter?: ConditionalValue<PropertyValueMap["breakAfter"] | AnyString>
  breakBefore?: ConditionalValue<PropertyValueMap["breakBefore"] | AnyString>
  breakInside?: ConditionalValue<PropertyValueMap["breakInside"] | AnyString>
  captionSide?: ConditionalValue<CssAny>
  caret?: ConditionalValue<PropertyValueMap["caret"]>
  caretColor?: ConditionalValue<PropertyValueMap["caretColor"]>
  caretShape?: ConditionalValue<CssAny>
  clear?: ConditionalValue<PropertyValueMap["clear"] | AnyString>
  clip?: ConditionalValue<CssAny>
  clipPath?: ConditionalValue<PropertyValueMap["clipPath"]>
  clipRule?: ConditionalValue<CssAny>
  color?: ConditionalValue<PropertyValueMap["color"]>
  colorInterpolation?: ConditionalValue<CssAny>
  colorInterpolationFilters?: ConditionalValue<CssAny>
  colorRendering?: ConditionalValue<CssAny>
  colorScheme?: ConditionalValue<PropertyValueMap["colorScheme"]>
  columnCount?: ConditionalValue<CssAny>
  columnFill?: ConditionalValue<CssAny>
  columnGap?: ConditionalValue<PropertyValueMap["columnGap"]>
  columnRule?: ConditionalValue<CssAny>
  columnRuleColor?: ConditionalValue<PropertyValueMap["columnRuleColor"]>
  columnRuleStyle?: ConditionalValue<PropertyValueMap["columnRuleStyle"]>
  columnRuleWidth?: ConditionalValue<PropertyValueMap["columnRuleWidth"]>
  columnSpan?: ConditionalValue<CssAny>
  columnWidth?: ConditionalValue<PropertyValueMap["columnWidth"]>
  columns?: ConditionalValue<CssAny>
  contain?: ConditionalValue<PropertyValueMap["contain"]>
  containIntrinsicBlockSize?: ConditionalValue<PropertyValueMap["containIntrinsicBlockSize"]>
  containIntrinsicHeight?: ConditionalValue<PropertyValueMap["containIntrinsicHeight"]>
  containIntrinsicInlineSize?: ConditionalValue<PropertyValueMap["containIntrinsicInlineSize"]>
  containIntrinsicSize?: ConditionalValue<PropertyValueMap["containIntrinsicSize"]>
  containIntrinsicWidth?: ConditionalValue<PropertyValueMap["containIntrinsicWidth"]>
  container?: ConditionalValue<CssContainer>
  containerName?: ConditionalValue<ContainerName>
  containerType?: ConditionalValue<PropertyValueMap["containerType"]>
  content?: ConditionalValue<PropertyValueMap["content"]>
  contentVisibility?: ConditionalValue<CssAny>
  counterIncrement?: ConditionalValue<CssAny>
  counterReset?: ConditionalValue<CssAny>
  counterSet?: ConditionalValue<CssAny>
  cursor?: ConditionalValue<PropertyValueMap["cursor"]>
  cx?: ConditionalValue<CssAny>
  cy?: ConditionalValue<CssAny>
  d?: ConditionalValue<CssAny>
  direction?: ConditionalValue<CssAny>
  display?: ConditionalValue<PropertyValueMap["display"]>
  dominantBaseline?: ConditionalValue<PropertyValueMap["dominantBaseline"] | AnyString>
  emptyCells?: ConditionalValue<CssAny>
  fieldSizing?: ConditionalValue<PropertyValueMap["fieldSizing"] | AnyString>
  fill?: ConditionalValue<CssAny>
  fillOpacity?: ConditionalValue<CssAny>
  fillRule?: ConditionalValue<CssAny>
  filter?: ConditionalValue<CssAny>
  flex?: ConditionalValue<CssAny>
  flexBasis?: ConditionalValue<PropertyValueMap["flexBasis"]>
  flexDirection?: ConditionalValue<CssAny>
  flexFlow?: ConditionalValue<PropertyValueMap["flexFlow"]>
  flexGrow?: ConditionalValue<PropertyValueMap["flexGrow"]>
  flexShrink?: ConditionalValue<PropertyValueMap["flexShrink"]>
  flexWrap?: ConditionalValue<CssAny>
  float?: ConditionalValue<PropertyValueMap["float"] | AnyString>
  floodColor?: ConditionalValue<PropertyValueMap["floodColor"]>
  floodOpacity?: ConditionalValue<CssAny>
  font?: ConditionalValue<PropertyValueMap["font"]>
  fontFamily?: ConditionalValue<PropertyValueMap["fontFamily"]>
  fontFeatureSettings?: ConditionalValue<CssAny>
  fontKerning?: ConditionalValue<CssAny>
  fontLanguageOverride?: ConditionalValue<CssAny>
  fontOpticalSizing?: ConditionalValue<CssAny>
  fontPalette?: ConditionalValue<CssAny>
  fontSize?: ConditionalValue<PropertyValueMap["fontSize"]>
  fontSizeAdjust?: ConditionalValue<PropertyValueMap["fontSizeAdjust"]>
  fontSmooth?: ConditionalValue<CssAny>
  fontStretch?: ConditionalValue<PropertyValueMap["fontStretch"]>
  fontStyle?: ConditionalValue<PropertyValueMap["fontStyle"]>
  fontSynthesis?: ConditionalValue<PropertyValueMap["fontSynthesis"]>
  fontSynthesisPosition?: ConditionalValue<CssAny>
  fontSynthesisSmallCaps?: ConditionalValue<CssAny>
  fontSynthesisStyle?: ConditionalValue<CssAny>
  fontSynthesisWeight?: ConditionalValue<CssAny>
  fontVariant?: ConditionalValue<CssAny>
  fontVariantAlternates?: ConditionalValue<CssAny>
  fontVariantCaps?: ConditionalValue<PropertyValueMap["fontVariantCaps"] | AnyString>
  fontVariantEastAsian?: ConditionalValue<PropertyValueMap["fontVariantEastAsian"]>
  fontVariantEmoji?: ConditionalValue<CssAny>
  fontVariantLigatures?: ConditionalValue<PropertyValueMap["fontVariantLigatures"]>
  fontVariantNumeric?: ConditionalValue<PropertyValueMap["fontVariantNumeric"]>
  fontVariantPosition?: ConditionalValue<CssAny>
  fontVariationSettings?: ConditionalValue<CssAny>
  fontWeight?: ConditionalValue<PropertyValueMap["fontWeight"]>
  fontWidth?: ConditionalValue<PropertyValueMap["fontWidth"]>
  forcedColorAdjust?: ConditionalValue<CssAny>
  gap?: ConditionalValue<PropertyValueMap["gap"]>
  glyphOrientationVertical?: ConditionalValue<CssAny>
  grid?: ConditionalValue<CssAny>
  gridArea?: ConditionalValue<CssAny>
  gridAutoColumns?: ConditionalValue<CssAny>
  gridAutoFlow?: ConditionalValue<PropertyValueMap["gridAutoFlow"]>
  gridAutoRows?: ConditionalValue<CssAny>
  gridColumn?: ConditionalValue<CssAny>
  gridColumnEnd?: ConditionalValue<CssAny>
  gridColumnGap?: ConditionalValue<PropertyValueMap["gridColumnGap"]>
  gridColumnStart?: ConditionalValue<CssAny>
  gridGap?: ConditionalValue<PropertyValueMap["gridGap"]>
  gridRow?: ConditionalValue<CssAny>
  gridRowEnd?: ConditionalValue<CssAny>
  gridRowGap?: ConditionalValue<PropertyValueMap["gridRowGap"]>
  gridRowStart?: ConditionalValue<CssAny>
  gridTemplate?: ConditionalValue<CssAny>
  gridTemplateAreas?: ConditionalValue<CssAny>
  gridTemplateColumns?: ConditionalValue<CssAny>
  gridTemplateRows?: ConditionalValue<CssAny>
  hangingPunctuation?: ConditionalValue<PropertyValueMap["hangingPunctuation"]>
  height?: ConditionalValue<PropertyValueMap["height"]>
  hyphenateCharacter?: ConditionalValue<CssAny>
  hyphenateLimitChars?: ConditionalValue<CssAny>
  hyphens?: ConditionalValue<PropertyValueMap["hyphens"] | AnyString>
  imageOrientation?: ConditionalValue<CssAny>
  imageRendering?: ConditionalValue<PropertyValueMap["imageRendering"] | AnyString>
  imageResolution?: ConditionalValue<CssAny>
  imeMode?: ConditionalValue<PropertyValueMap["imeMode"] | AnyString>
  initialLetter?: ConditionalValue<CssAny>
  initialLetterAlign?: ConditionalValue<CssAny>
  inlineSize?: ConditionalValue<PropertyValueMap["inlineSize"]>
  inset?: ConditionalValue<PropertyValueMap["inset"]>
  insetBlock?: ConditionalValue<CssAny>
  insetBlockEnd?: ConditionalValue<CssAny>
  insetBlockStart?: ConditionalValue<CssAny>
  insetInline?: ConditionalValue<CssAny>
  insetInlineEnd?: ConditionalValue<CssAny>
  insetInlineStart?: ConditionalValue<CssAny>
  interpolateSize?: ConditionalValue<CssAny>
  isolation?: ConditionalValue<CssAny>
  justifyContent?: ConditionalValue<PropertyValueMap["justifyContent"]>
  justifyItems?: ConditionalValue<PropertyValueMap["justifyItems"]>
  justifySelf?: ConditionalValue<PropertyValueMap["justifySelf"]>
  justifyTracks?: ConditionalValue<CssAny>
  left?: ConditionalValue<PropertyValueMap["left"]>
  letterSpacing?: ConditionalValue<PropertyValueMap["letterSpacing"]>
  lightingColor?: ConditionalValue<PropertyValueMap["lightingColor"]>
  lineBreak?: ConditionalValue<PropertyValueMap["lineBreak"] | AnyString>
  lineClamp?: ConditionalValue<CssAny>
  lineHeight?: ConditionalValue<PropertyValueMap["lineHeight"]>
  lineHeightStep?: ConditionalValue<PropertyValueMap["lineHeightStep"]>
  listStyle?: ConditionalValue<CssAny>
  listStyleImage?: ConditionalValue<PropertyValueMap["listStyleImage"]>
  listStylePosition?: ConditionalValue<PropertyValueMap["listStylePosition"] | AnyString>
  listStyleType?: ConditionalValue<PropertyValueMap["listStyleType"]>
  margin?: ConditionalValue<PropertyValueMap["margin"]>
  marginBlock?: ConditionalValue<CssAny>
  marginBlockEnd?: ConditionalValue<CssAny>
  marginBlockStart?: ConditionalValue<CssAny>
  marginBottom?: ConditionalValue<PropertyValueMap["marginBottom"]>
  marginInline?: ConditionalValue<CssAny>
  marginInlineEnd?: ConditionalValue<CssAny>
  marginInlineStart?: ConditionalValue<CssAny>
  marginLeft?: ConditionalValue<PropertyValueMap["marginLeft"]>
  marginRight?: ConditionalValue<PropertyValueMap["marginRight"]>
  marginTop?: ConditionalValue<PropertyValueMap["marginTop"]>
  marginTrim?: ConditionalValue<CssAny>
  marker?: ConditionalValue<CssAny>
  markerEnd?: ConditionalValue<CssAny>
  markerMid?: ConditionalValue<CssAny>
  markerStart?: ConditionalValue<CssAny>
  mask?: ConditionalValue<CssAny>
  maskBorder?: ConditionalValue<PropertyValueMap["maskBorder"]>
  maskBorderMode?: ConditionalValue<CssAny>
  maskBorderOutset?: ConditionalValue<CssAny>
  maskBorderRepeat?: ConditionalValue<CssAny>
  maskBorderSlice?: ConditionalValue<CssAny>
  maskBorderSource?: ConditionalValue<CssAny>
  maskBorderWidth?: ConditionalValue<PropertyValueMap["maskBorderWidth"]>
  maskClip?: ConditionalValue<CssAny>
  maskComposite?: ConditionalValue<CssAny>
  maskImage?: ConditionalValue<CssAny>
  maskMode?: ConditionalValue<CssAny>
  maskOrigin?: ConditionalValue<CssAny>
  maskPosition?: ConditionalValue<PropertyValueMap["maskPosition"]>
  maskRepeat?: ConditionalValue<PropertyValueMap["maskRepeat"]>
  maskSize?: ConditionalValue<PropertyValueMap["maskSize"]>
  maskType?: ConditionalValue<CssAny>
  masonryAutoFlow?: ConditionalValue<CssAny>
  mathDepth?: ConditionalValue<CssAny>
  mathShift?: ConditionalValue<CssAny>
  mathStyle?: ConditionalValue<CssAny>
  maxBlockSize?: ConditionalValue<PropertyValueMap["maxBlockSize"]>
  maxHeight?: ConditionalValue<PropertyValueMap["maxHeight"]>
  maxInlineSize?: ConditionalValue<PropertyValueMap["maxInlineSize"]>
  maxLines?: ConditionalValue<CssAny>
  maxWidth?: ConditionalValue<PropertyValueMap["maxWidth"]>
  minBlockSize?: ConditionalValue<PropertyValueMap["minBlockSize"]>
  minHeight?: ConditionalValue<PropertyValueMap["minHeight"]>
  minInlineSize?: ConditionalValue<PropertyValueMap["minInlineSize"]>
  minWidth?: ConditionalValue<PropertyValueMap["minWidth"]>
  mixBlendMode?: ConditionalValue<PropertyValueMap["mixBlendMode"] | AnyString>
  objectFit?: ConditionalValue<PropertyValueMap["objectFit"] | AnyString>
  objectPosition?: ConditionalValue<PropertyValueMap["objectPosition"]>
  objectViewBox?: ConditionalValue<CssAny>
  offset?: ConditionalValue<CssAny>
  offsetAnchor?: ConditionalValue<PropertyValueMap["offsetAnchor"]>
  offsetDistance?: ConditionalValue<CssAny>
  offsetPath?: ConditionalValue<CssAny>
  offsetPosition?: ConditionalValue<PropertyValueMap["offsetPosition"]>
  offsetRotate?: ConditionalValue<CssAny>
  opacity?: ConditionalValue<PropertyValueMap["opacity"]>
  order?: ConditionalValue<PropertyValueMap["order"]>
  orphans?: ConditionalValue<PropertyValueMap["orphans"]>
  outline?: ConditionalValue<CssAny>
  outlineColor?: ConditionalValue<PropertyValueMap["outlineColor"]>
  outlineOffset?: ConditionalValue<PropertyValueMap["outlineOffset"]>
  outlineStyle?: ConditionalValue<PropertyValueMap["outlineStyle"] | AnyString>
  outlineWidth?: ConditionalValue<PropertyValueMap["outlineWidth"]>
  overflow?: ConditionalValue<PropertyValueMap["overflow"]>
  overflowAnchor?: ConditionalValue<CssAny>
  overflowBlock?: ConditionalValue<PropertyValueMap["overflowBlock"] | AnyString>
  overflowClipBox?: ConditionalValue<CssAny>
  overflowClipMargin?: ConditionalValue<PropertyValueMap["overflowClipMargin"]>
  overflowInline?: ConditionalValue<PropertyValueMap["overflowInline"] | AnyString>
  overflowWrap?: ConditionalValue<CssAny>
  overflowX?: ConditionalValue<PropertyValueMap["overflowX"] | AnyString>
  overflowY?: ConditionalValue<PropertyValueMap["overflowY"] | AnyString>
  overlay?: ConditionalValue<CssAny>
  overscrollBehavior?: ConditionalValue<PropertyValueMap["overscrollBehavior"]>
  overscrollBehaviorBlock?: ConditionalValue<CssAny>
  overscrollBehaviorInline?: ConditionalValue<CssAny>
  overscrollBehaviorX?: ConditionalValue<PropertyValueMap["overscrollBehaviorX"] | AnyString>
  overscrollBehaviorY?: ConditionalValue<PropertyValueMap["overscrollBehaviorY"] | AnyString>
  padding?: ConditionalValue<PropertyValueMap["padding"]>
  paddingBlock?: ConditionalValue<CssAny>
  paddingBlockEnd?: ConditionalValue<CssAny>
  paddingBlockStart?: ConditionalValue<CssAny>
  paddingBottom?: ConditionalValue<PropertyValueMap["paddingBottom"]>
  paddingInline?: ConditionalValue<CssAny>
  paddingInlineEnd?: ConditionalValue<CssAny>
  paddingInlineStart?: ConditionalValue<CssAny>
  paddingLeft?: ConditionalValue<PropertyValueMap["paddingLeft"]>
  paddingRight?: ConditionalValue<PropertyValueMap["paddingRight"]>
  paddingTop?: ConditionalValue<PropertyValueMap["paddingTop"]>
  page?: ConditionalValue<CssAny>
  pageBreakAfter?: ConditionalValue<PropertyValueMap["pageBreakAfter"] | AnyString>
  pageBreakBefore?: ConditionalValue<PropertyValueMap["pageBreakBefore"] | AnyString>
  pageBreakInside?: ConditionalValue<CssAny>
  paintOrder?: ConditionalValue<CssAny>
  perspective?: ConditionalValue<PropertyValueMap["perspective"]>
  perspectiveOrigin?: ConditionalValue<PropertyValueMap["perspectiveOrigin"]>
  placeContent?: ConditionalValue<PropertyValueMap["placeContent"]>
  placeItems?: ConditionalValue<PropertyValueMap["placeItems"]>
  placeSelf?: ConditionalValue<PropertyValueMap["placeSelf"]>
  pointerEvents?: ConditionalValue<PropertyValueMap["pointerEvents"] | AnyString>
  position?: ConditionalValue<PropertyValueMap["position"] | AnyString>
  positionAnchor?: ConditionalValue<CssAny>
  positionArea?: ConditionalValue<CssAny>
  positionTry?: ConditionalValue<CssAny>
  positionTryFallbacks?: ConditionalValue<CssAny>
  positionTryOrder?: ConditionalValue<PropertyValueMap["positionTryOrder"] | AnyString>
  positionVisibility?: ConditionalValue<CssAny>
  printColorAdjust?: ConditionalValue<CssAny>
  quotes?: ConditionalValue<CssAny>
  r?: ConditionalValue<CssAny>
  resize?: ConditionalValue<PropertyValueMap["resize"] | AnyString>
  right?: ConditionalValue<PropertyValueMap["right"]>
  rotate?: ConditionalValue<CssAny>
  rowGap?: ConditionalValue<PropertyValueMap["rowGap"]>
  rubyAlign?: ConditionalValue<CssAny>
  rubyMerge?: ConditionalValue<CssAny>
  rubyOverhang?: ConditionalValue<CssAny>
  rubyPosition?: ConditionalValue<CssAny>
  rx?: ConditionalValue<CssAny>
  ry?: ConditionalValue<CssAny>
  scale?: ConditionalValue<CssAny>
  scrollBehavior?: ConditionalValue<CssAny>
  scrollInitialTarget?: ConditionalValue<CssAny>
  scrollMargin?: ConditionalValue<CssAny>
  scrollMarginBlock?: ConditionalValue<PropertyValueMap["scrollMarginBlock"]>
  scrollMarginBlockEnd?: ConditionalValue<PropertyValueMap["scrollMarginBlockEnd"]>
  scrollMarginBlockStart?: ConditionalValue<PropertyValueMap["scrollMarginBlockStart"]>
  scrollMarginBottom?: ConditionalValue<PropertyValueMap["scrollMarginBottom"]>
  scrollMarginInline?: ConditionalValue<PropertyValueMap["scrollMarginInline"]>
  scrollMarginInlineEnd?: ConditionalValue<PropertyValueMap["scrollMarginInlineEnd"]>
  scrollMarginInlineStart?: ConditionalValue<PropertyValueMap["scrollMarginInlineStart"]>
  scrollMarginLeft?: ConditionalValue<PropertyValueMap["scrollMarginLeft"]>
  scrollMarginRight?: ConditionalValue<PropertyValueMap["scrollMarginRight"]>
  scrollMarginTop?: ConditionalValue<PropertyValueMap["scrollMarginTop"]>
  scrollPadding?: ConditionalValue<CssAny>
  scrollPaddingBlock?: ConditionalValue<PropertyValueMap["scrollPaddingBlock"]>
  scrollPaddingBlockEnd?: ConditionalValue<PropertyValueMap["scrollPaddingBlockEnd"]>
  scrollPaddingBlockStart?: ConditionalValue<PropertyValueMap["scrollPaddingBlockStart"]>
  scrollPaddingBottom?: ConditionalValue<PropertyValueMap["scrollPaddingBottom"]>
  scrollPaddingInline?: ConditionalValue<PropertyValueMap["scrollPaddingInline"]>
  scrollPaddingInlineEnd?: ConditionalValue<PropertyValueMap["scrollPaddingInlineEnd"]>
  scrollPaddingInlineStart?: ConditionalValue<PropertyValueMap["scrollPaddingInlineStart"]>
  scrollPaddingLeft?: ConditionalValue<PropertyValueMap["scrollPaddingLeft"]>
  scrollPaddingRight?: ConditionalValue<PropertyValueMap["scrollPaddingRight"]>
  scrollPaddingTop?: ConditionalValue<PropertyValueMap["scrollPaddingTop"]>
  scrollSnapAlign?: ConditionalValue<PropertyValueMap["scrollSnapAlign"]>
  scrollSnapCoordinate?: ConditionalValue<CssAny>
  scrollSnapDestination?: ConditionalValue<PropertyValueMap["scrollSnapDestination"]>
  scrollSnapPointsX?: ConditionalValue<CssAny>
  scrollSnapPointsY?: ConditionalValue<CssAny>
  scrollSnapStop?: ConditionalValue<PropertyValueMap["scrollSnapStop"] | AnyString>
  scrollSnapType?: ConditionalValue<PropertyValueMap["scrollSnapType"]>
  scrollSnapTypeX?: ConditionalValue<CssAny>
  scrollSnapTypeY?: ConditionalValue<CssAny>
  scrollTimeline?: ConditionalValue<CssAny>
  scrollTimelineAxis?: ConditionalValue<CssAny>
  scrollTimelineName?: ConditionalValue<CssAny>
  scrollbarColor?: ConditionalValue<CssAny>
  scrollbarGutter?: ConditionalValue<PropertyValueMap["scrollbarGutter"]>
  scrollbarWidth?: ConditionalValue<PropertyValueMap["scrollbarWidth"] | AnyString>
  shapeImageThreshold?: ConditionalValue<CssAny>
  shapeMargin?: ConditionalValue<PropertyValueMap["shapeMargin"]>
  shapeOutside?: ConditionalValue<PropertyValueMap["shapeOutside"]>
  shapeRendering?: ConditionalValue<CssAny>
  speakAs?: ConditionalValue<PropertyValueMap["speakAs"]>
  stopColor?: ConditionalValue<PropertyValueMap["stopColor"]>
  stopOpacity?: ConditionalValue<CssAny>
  stroke?: ConditionalValue<CssAny>
  strokeColor?: ConditionalValue<PropertyValueMap["strokeColor"]>
  strokeDasharray?: ConditionalValue<CssAny>
  strokeDashoffset?: ConditionalValue<CssAny>
  strokeLinecap?: ConditionalValue<CssAny>
  strokeLinejoin?: ConditionalValue<PropertyValueMap["strokeLinejoin"] | AnyString>
  strokeMiterlimit?: ConditionalValue<CssAny>
  strokeOpacity?: ConditionalValue<CssAny>
  strokeWidth?: ConditionalValue<PropertyValueMap["strokeWidth"]>
  tabSize?: ConditionalValue<PropertyValueMap["tabSize"]>
  tableLayout?: ConditionalValue<PropertyValueMap["tableLayout"] | AnyString>
  textAlign?: ConditionalValue<PropertyValueMap["textAlign"] | AnyString>
  textAlignLast?: ConditionalValue<PropertyValueMap["textAlignLast"] | AnyString>
  textAnchor?: ConditionalValue<CssAny>
  textAutospace?: ConditionalValue<PropertyValueMap["textAutospace"]>
  textBox?: ConditionalValue<PropertyValueMap["textBox"]>
  textBoxEdge?: ConditionalValue<PropertyValueMap["textBoxEdge"]>
  textBoxTrim?: ConditionalValue<CssAny>
  textCombineUpright?: ConditionalValue<CssAny>
  textDecoration?: ConditionalValue<CssAny>
  textDecorationColor?: ConditionalValue<PropertyValueMap["textDecorationColor"]>
  textDecorationLine?: ConditionalValue<PropertyValueMap["textDecorationLine"]>
  textDecorationSkip?: ConditionalValue<PropertyValueMap["textDecorationSkip"]>
  textDecorationSkipInk?: ConditionalValue<PropertyValueMap["textDecorationSkipInk"] | AnyString>
  textDecorationStyle?: ConditionalValue<PropertyValueMap["textDecorationStyle"] | AnyString>
  textDecorationThickness?: ConditionalValue<PropertyValueMap["textDecorationThickness"]>
  textEmphasis?: ConditionalValue<PropertyValueMap["textEmphasis"]>
  textEmphasisColor?: ConditionalValue<PropertyValueMap["textEmphasisColor"]>
  textEmphasisPosition?: ConditionalValue<PropertyValueMap["textEmphasisPosition"]>
  textEmphasisStyle?: ConditionalValue<PropertyValueMap["textEmphasisStyle"]>
  textIndent?: ConditionalValue<PropertyValueMap["textIndent"]>
  textJustify?: ConditionalValue<PropertyValueMap["textJustify"] | AnyString>
  textOrientation?: ConditionalValue<PropertyValueMap["textOrientation"] | AnyString>
  textOverflow?: ConditionalValue<PropertyValueMap["textOverflow"]>
  textRendering?: ConditionalValue<PropertyValueMap["textRendering"] | AnyString>
  textShadow?: ConditionalValue<CssAny>
  textSizeAdjust?: ConditionalValue<PropertyValueMap["textSizeAdjust"]>
  textSpacingTrim?: ConditionalValue<CssAny>
  textTransform?: ConditionalValue<PropertyValueMap["textTransform"]>
  textUnderlineOffset?: ConditionalValue<PropertyValueMap["textUnderlineOffset"]>
  textUnderlinePosition?: ConditionalValue<PropertyValueMap["textUnderlinePosition"]>
  textWrap?: ConditionalValue<PropertyValueMap["textWrap"]>
  textWrapMode?: ConditionalValue<PropertyValueMap["textWrapMode"] | AnyString>
  textWrapStyle?: ConditionalValue<PropertyValueMap["textWrapStyle"] | AnyString>
  timelineScope?: ConditionalValue<CssAny>
  top?: ConditionalValue<PropertyValueMap["top"]>
  touchAction?: ConditionalValue<PropertyValueMap["touchAction"]>
  transform?: ConditionalValue<CssAny>
  transformBox?: ConditionalValue<PropertyValueMap["transformBox"] | AnyString>
  transformOrigin?: ConditionalValue<CssAny>
  transformStyle?: ConditionalValue<CssAny>
  transition?: ConditionalValue<CssAny>
  transitionBehavior?: ConditionalValue<PropertyValueMap["transitionBehavior"]>
  transitionDelay?: ConditionalValue<CssAny>
  transitionDuration?: ConditionalValue<CssAny>
  transitionProperty?: ConditionalValue<PropertyValueMap["transitionProperty"]>
  transitionTimingFunction?: ConditionalValue<CssAny>
  translate?: ConditionalValue<CssAny>
  unicodeBidi?: ConditionalValue<PropertyValueMap["unicodeBidi"] | AnyString>
  userSelect?: ConditionalValue<PropertyValueMap["userSelect"] | AnyString>
  vectorEffect?: ConditionalValue<PropertyValueMap["vectorEffect"] | AnyString>
  verticalAlign?: ConditionalValue<PropertyValueMap["verticalAlign"]>
  viewTimeline?: ConditionalValue<CssAny>
  viewTimelineAxis?: ConditionalValue<CssAny>
  viewTimelineInset?: ConditionalValue<PropertyValueMap["viewTimelineInset"]>
  viewTimelineName?: ConditionalValue<CssAny>
  viewTransitionClass?: ConditionalValue<CssAny>
  viewTransitionName?: ConditionalValue<CssAny>
  visibility?: ConditionalValue<CssAny>
  whiteSpace?: ConditionalValue<PropertyValueMap["whiteSpace"]>
  whiteSpaceCollapse?: ConditionalValue<PropertyValueMap["whiteSpaceCollapse"] | AnyString>
  widows?: ConditionalValue<PropertyValueMap["widows"]>
  width?: ConditionalValue<PropertyValueMap["width"]>
  willChange?: ConditionalValue<CssAny>
  wordBreak?: ConditionalValue<PropertyValueMap["wordBreak"] | AnyString>
  wordSpacing?: ConditionalValue<PropertyValueMap["wordSpacing"]>
  wordWrap?: ConditionalValue<PropertyValueMap["wordWrap"] | AnyString>
  writingMode?: ConditionalValue<PropertyValueMap["writingMode"] | AnyString>
  x?: ConditionalValue<CssAny>
  y?: ConditionalValue<CssAny>
  zIndex?: ConditionalValue<PropertyValueMap["zIndex"]>
  zoom?: ConditionalValue<PropertyValueMap["zoom"]>
  colorPalette?: ConditionalValue<ColorPaletteValue | CssAny>
}

export type CssVarValue = ConditionalValue<CssVars | AnyString | AnyNumber>

export type CssVarProperties = {
  [K in `--${string}`]?: CssVarValue
}

export type NestedStyles = {
  [K in Selector | Condition]?: SystemStyleObject
}

export interface SystemStyleObject extends SystemProperties, CssVarProperties, NestedStyles {}

export type SystemStyleObjectWith<K extends keyof SystemProperties> = Pick<SystemProperties, K> & {
  [S in Selector | Condition]?: SystemStyleObjectWith<K>
}

export type SystemStyleObjectWithout<K extends keyof SystemProperties> = SystemStyleObjectWith<Exclude<keyof SystemProperties, K>>

export interface GlobalStyleObject {
  [selector: string]: SystemStyleObject
}

export interface CssKeyframes {
  [name: string]: {
    [time: string]: SystemStyleObject
  }
}

export interface GlobalFontfaceRule {
  fontFamily: string
  src: string
  fontStyle?: string
  fontWeight?: string | number
  fontDisplay?: "auto" | "block" | "swap" | "fallback" | "optional"
  unicodeRange?: string
  fontFeatureSettings?: string
  fontVariationSettings?: string
  fontStretch?: string
  ascentOverride?: string
  descentOverride?: string
  lineGapOverride?: string
  sizeAdjust?: string
}

export type FontfaceRule = Omit<GlobalFontfaceRule, "fontFamily">

export interface GlobalFontface {
  [name: string]: FontfaceRule | FontfaceRule[]
}

interface WithCss {
  css?: SystemStyleObject | SystemStyleObject[]
}

export type JsxStyleProps = SystemStyleObject & WithCss

export interface PatchedHTMLProps {
  htmlWidth?: string | number
  htmlHeight?: string | number
  htmlTranslate?: "yes" | "no" | undefined
  htmlContent?: string
}

export type OmittedHTMLProps = "color" | "translate" | "transition" | "width" | "height" | "content"

type WithHTMLProps<T> = DistributiveOmit<T, OmittedHTMLProps> & PatchedHTMLProps

export type JsxHTMLProps<T extends Record<string, any>, P extends Record<string, any> = {}> = Assign<WithHTMLProps<T>, P>