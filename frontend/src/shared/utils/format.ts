const AMOUNT_PATTERN = /^(-?)(\d+)(?:\.(\d+))?$/

/** Formate un montant décimal de l'API sans conversion flottante ni conversion de devise. */
export function formatMoney(amount: string, currency: string): string {
  const raw = String(amount).trim()
  const match = AMOUNT_PATTERN.exec(raw)
  if (!match) return `${raw} ${currency}`
  const [, sign, integer, fraction = ''] = match
  const grouped = integer.replace(/\B(?=(\d{3})+(?!\d))/g, '\u202f')
  return `${sign}${grouped},${fraction.padEnd(2, '0')}\u00a0${currency}`
}

/** 2026-10-31 -> 31/10/2026 (sans passer par Date, donc sans décalage de fuseau). */
export function formatDate(value: string): string {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value)
  return match ? `${match[3]}/${match[2]}/${match[1]}` : value
}

export function formatDateTime(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('fr-FR', { dateStyle: 'short', timeStyle: 'short' }).format(date)
}