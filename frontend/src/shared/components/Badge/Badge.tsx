import type { HTMLAttributes, ReactNode } from 'react'
import { css, cx } from '../../../../styled-system/css'
import { token } from '../../../../styled-system/tokens'

export type BadgeVariant = 'default' | 'success' | 'warning' | 'danger' | 'info'

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant
  children: ReactNode
  className?: string
}

const badgeStyle = css({
  display: 'inline-flex',
  alignItems: 'center',
  fontWeight: '600',
  borderRadius: token.var('radii.sm'),
  paddingLeft: token.var('spacing.2'),
  paddingRight: token.var('spacing.2'),
  paddingTop: token.var('spacing.1'),
  paddingBottom: token.var('spacing.1'),
  fontSize: token.var('fontSizes.xs'),
  lineHeight: 'var(--line-height-tight)',
  letterSpacing: '0.02em',
  whiteSpace: 'nowrap',
  transition: 'background-color 150ms ease, color 150ms ease',
})

const variantStyles: Record<BadgeVariant, string> = {
  default: css({
    backgroundColor: token.var('colors.surface.subtle'),
    color: token.var('colors.text.main'),
    border: '1px solid',
    borderColor: token.var('colors.surface.border'),
  }),
  info: css({
    backgroundColor: token.var('colors.brand.primarySoft'),
    color: token.var('colors.brand.primary'),
    border: '1px solid',
    borderColor: 'rgba(18, 59, 74, 0.18)',
  }),
  success: css({
    backgroundColor: 'rgba(36, 122, 82, 0.10)',
    color: token.var('colors.status.success'),
    border: '1px solid',
    borderColor: 'rgba(36, 122, 82, 0.22)',
  }),
  warning: css({
    backgroundColor: 'rgba(166, 106, 0, 0.10)',
    color: token.var('colors.status.warning'),
    border: '1px solid',
    borderColor: 'rgba(166, 106, 0, 0.22)',
  }),
  danger: css({
    backgroundColor: 'rgba(180, 35, 24, 0.10)',
    color: token.var('colors.status.danger'),
    border: '1px solid',
    borderColor: 'rgba(180, 35, 24, 0.22)',
  }),
}

export function Badge({
  variant = 'default',
  children,
  className,
  ...rest
}: BadgeProps) {
  return (
    <span
      className={cx(badgeStyle, variantStyles[variant], className)}
      {...rest}
    >
      {children}
    </span>
  )
}
