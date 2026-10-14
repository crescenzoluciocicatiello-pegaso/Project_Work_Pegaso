type DataInput = string | Date | null | undefined

// le date "YYYY-MM-DD" senza orario le leggo come ora locale, altrimenti new Date le prende in UTC
function toDate(value: DataInput) {
  if (!value) return null
  const data = new Date(typeof value === 'string' && value.length === 10 ? `${value}T00:00` : value)
  return isNaN(data.getTime()) ? null : data
}

export function formatData(value: DataInput) {
  const data = toDate(value)
  if (!data) return '-'
  return data.toLocaleDateString('it-IT', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

export function formatOra(value: DataInput) {
  const data = toDate(value)
  if (!data) return '-'
  return data.toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' })
}

export function formatGiorno(value: DataInput) {
  const data = toDate(value)
  if (!data) return '-'
  return data.toLocaleDateString('it-IT', { weekday: 'long' })
}

export function formatDataOra(value: DataInput) {
  if (!toDate(value)) return '-'
  return formatData(value) + ' ' + formatOra(value)
}
