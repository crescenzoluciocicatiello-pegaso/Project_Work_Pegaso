<script setup lang="ts">
const api = useApi()

const authCookie = useCookie<any>('auth_user')
const pazienteId = authCookie.value?.id ?? null

// la prenotazione da mostrare la salva la dashboard in questo cookie
const resocontoCookie = useCookie<{ id_prenotazione: number } | null>('resoconto_prenotazione')
const prenotazioneId = resocontoCookie.value?.id_prenotazione ?? null

const prenotazione = ref<any>(null)

// non c'è un endpoint per la singola prenotazione, la cerco tra quelle del paziente
try {
  const lista = await api<any[]>(`/prenotazioni/paziente/${pazienteId}`)
  prenotazione.value = lista.find((p) => p.id === prenotazioneId) ?? null
} catch (err) {
  console.error(err)
}

const stato = computed(() =>
  prenotazione.value?.stato_pren === STATO_PRENOTAZIONE_CONFERMATA
    ? 'Confermata'
    : prenotazione.value?.stato_pren
)

const datiPaziente = computed(() => {
  const p = prenotazione.value
  return [
    { label: 'Nome e cognome', valore: `${p.nome} ${p.cognome}` },
    { label: 'Codice fiscale', valore: p.codice_fiscale },
    { label: 'Data di nascita', valore: formatData(p.data_nascita) },
    { label: 'Comune di nascita', valore: p.comune_nascita ?? '-' }
  ]
})

const datiAppuntamento = computed(() => {
  const p = prenotazione.value
  return [
    { label: 'Prestazione', valore: `${p.codice_prestazione} - ${p.descrizione}` },
    {
      label: 'Giorno',
      valore: `${formatGiorno(p.data_inizio_slot)} ${formatData(p.data_inizio_slot)}`
    },
    {
      label: 'Orario',
      valore: `dalle ${formatOra(p.data_inizio_slot)} alle ${formatOra(p.data_fine_slot)}`
    },
    { label: 'Prenotata il', valore: formatDataOra(p.data_prenotazione) },
    { label: 'Note', valore: p.note_paziente || '-' }
  ]
})

function stampa() {
  window.print()
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-2 print:hidden">
      <NuxtLink to="/dashboard_paziente" class="text-sm font-semibold text-primary hover:underline">
        &larr; Torna alle mie prenotazioni
      </NuxtLink>
      <UButton v-if="prenotazione" label="Stampa" icon="i-lucide-printer" @click="stampa" />
    </div>

    <UAlert
      v-if="!prenotazione"
      icon="i-lucide-info"
      color="warning"
      variant="subtle"
      title="Prenotazione non trovata"
    />

    <UCard v-else class="mx-auto max-w-3xl print:shadow-none">
      <template #header>
        <AppLogo />
      </template>

      <div class="space-y-6">
        <div class="flex flex-wrap items-center gap-3">
          <h1 class="text-xl font-bold text-highlighted">Resoconto della prenotazione</h1>
          <UBadge :label="stato" variant="subtle" />
        </div>

        <div>
          <h2 class="mb-3 font-semibold text-primary">Paziente</h2>
          <dl class="grid gap-4 text-sm sm:grid-cols-2">
            <div v-for="dato in datiPaziente" :key="dato.label">
              <dt class="text-muted">{{ dato.label }}</dt>
              <dd class="font-semibold">{{ dato.valore }}</dd>
            </div>
          </dl>
        </div>

        <div>
          <h2 class="mb-3 font-semibold text-primary">Appuntamento</h2>
          <dl class="grid gap-4 text-sm sm:grid-cols-2">
            <div v-for="dato in datiAppuntamento" :key="dato.label">
              <dt class="text-muted">{{ dato.label }}</dt>
              <dd class="font-semibold">{{ dato.valore }}</dd>
            </div>
          </dl>
        </div>

        <UAlert
          icon="i-lucide-info"
          color="neutral"
          variant="subtle"
          description="Il giorno dell'appuntamento porta con te questo foglio, la ricetta e la tessera sanitaria."
        />
      </div>
    </UCard>
  </div>
</template>
