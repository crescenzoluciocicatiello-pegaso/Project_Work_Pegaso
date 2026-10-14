// NRE: 15 caratteri, mostrato come "ABCDE 1234567890"
export const formattaNre = (valore: string | null | undefined) => {
  const caratteri = (valore ?? '')
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, '')
    .slice(0, 15)
  return caratteri.length > 5 ? `${caratteri.slice(0, 5)} ${caratteri.slice(5)}` : caratteri
}

export const STATO_PRENOTAZIONE_CONFERMATA = '1'
