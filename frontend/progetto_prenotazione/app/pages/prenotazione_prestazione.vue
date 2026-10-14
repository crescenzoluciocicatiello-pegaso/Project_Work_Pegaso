<script setup lang="ts">
const toast = useToast()
const api = useApi()

// la ricetta da aprire la salva la dashboard in questo cookie
const prenotazioneCookie = useCookie<{ id_ricetta: number; id_paziente: number | null } | null>(
  'prenotazione_prestazione'
)
const ricettaId = prenotazioneCookie.value?.id_ricetta ?? null
const pazienteId = prenotazioneCookie.value?.id_paziente ?? null

const ricetta = ref<any>(null)
const prestazioni = ref<any[]>([])
const caricamento = ref(true)

const colonne = [
  { accessorKey: 'codice_prestazione', header: 'Codice' },
  { accessorKey: 'descrizione', header: 'Prestazione' },
  { id: 'azioni', header: '' }
]

const numeroPrenotate = computed(() => prestazioni.value.filter((p) => p.prenotata).length)

// modale orari
const modaleAperta = ref(false)
const prestazioneScelta = ref<any>(null)
const slotLiberi = ref<any[]>([])
const caricamentoSlot = ref(false)
const slotScelto = ref<any>(null)
const notePaziente = ref('')

// slot raggruppati per giorno
const slotPerGiorno = computed(() => {
  const gruppi = new Map<string, any[]>()
  const ordinati = [...slotLiberi.value].sort((a, b) =>
    a.data_inizio_slot.localeCompare(b.data_inizio_slot)
  )
  for (const slot of ordinati) {
    const giorno = slot.data_inizio_slot.slice(0, 10)
    if (!gruppi.has(giorno)) gruppi.set(giorno, [])
    gruppi.get(giorno)!.push(slot)
  }
  return gruppi
})

async function caricaPrestazioni() {
  try {
    prestazioni.value = await api(`/ricetta-prestazione/${ricettaId}`)
  } catch (err) {
    console.error(err)
  }
}

async function apriModale(prestazione: any) {
  prestazioneScelta.value = prestazione
  slotScelto.value = null
  notePaziente.value = ''
  slotLiberi.value = []
  modaleAperta.value = true
  caricamentoSlot.value = true
  try {
    slotLiberi.value = await api('/slot/disponibili-by-codice-prestazione', {
      query: { id_prestazione: prestazione.id_prestazione }
    })
  } catch (err) {
    console.error(err)
  } finally {
    caricamentoSlot.value = false
  }
}

async function confermaPrenotazione() {
  try {
    await api('/prenotazioni/', {
      method: 'POST',
      body: {
        note_paziente: notePaziente.value.trim(),
        stato_pren: STATO_PRENOTAZIONE_CONFERMATA,
        id_paziente: pazienteId,
        id_ricetta_prestazione: prestazioneScelta.value.id,
        id_slot: slotScelto.value.id
      }
    })
    toast.add({ title: 'Prenotazione effettuata', color: 'success' })
    modaleAperta.value = false
  } catch (err) {
    console.error(err)
    toast.add({ title: 'Impossibile completare la prenotazione', color: 'error' })
  }
  await caricaPrestazioni()
}

async function eliminaPrenotazione(prestazione: any) {
  const conferma = window.confirm(
    `Vuoi eliminare la prenotazione di "${prestazione.codice_prestazione} - ${prestazione.descrizione}"?`
  )
  if (!conferma) return

  try {
    await api(`/prenotazioni/ricetta-prestazione/${prestazione.id}`, { method: 'DELETE' })
    toast.add({ title: 'Prenotazione eliminata', color: 'success' })
  } catch (err) {
    console.error(err)
    toast.add({ title: 'Impossibile eliminare la prenotazione', color: 'error' })
  }
  await caricaPrestazioni()
}

onMounted(async () => {
  if (ricettaId) {
    try {
      const [datiRicetta] = await Promise.all([api(`/ricette/${ricettaId}`), caricaPrestazioni()])
      ricetta.value = datiRicetta
    } catch (err) {
      console.error(err)
    }
  }
  caricamento.value = false
})
</script>

<template>
  <div class="space-y-6">
    <div>
      <NuxtLink to="/dashboard_paziente" class="text-sm font-semibold text-primary hover:underline">
        &larr; Torna alle mie ricette
      </NuxtLink>
      <h1 class="mt-2 text-2xl font-bold text-highlighted">Prenota le prestazioni</h1>
      <p class="text-muted">Scegli una prestazione della ricetta e poi un orario libero.</p>
    </div>

    <p v-if="caricamento" class="text-muted">Caricamento in corso...</p>

    <UAlert
      v-else-if="!ricetta"
      icon="i-lucide-info"
      color="warning"
      variant="subtle"
      title="Nessuna ricetta selezionata"
      description='Torna alla pagina delle ricette e premi "Prenota" su una ricetta.'
    />

    <template v-else>
      <UCard>
        <h2 class="mb-3 text-lg font-bold text-primary">Dati della ricetta</h2>
        <dl class="grid gap-4 text-sm sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <dt class="text-muted">Numero ricetta</dt>
            <dd class="font-mono font-semibold">{{ formattaNre(ricetta.nre) }}</dd>
          </div>
          <div>
            <dt class="text-muted">Medico</dt>
            <dd class="font-semibold">{{ ricetta.nome_medico ?? '-' }}</dd>
          </div>
          <div>
            <dt class="text-muted">Data di emissione</dt>
            <dd class="font-semibold">{{ formatData(ricetta.data_emissione) }}</dd>
          </div>
          <div>
            <dt class="text-muted">Data di scadenza</dt>
            <dd class="font-semibold">{{ formatData(ricetta.data_scadenza) }}</dd>
          </div>
        </dl>
      </UCard>

      <UCard>
        <div class="mb-2 flex flex-wrap items-center justify-between gap-2">
          <h2 class="text-lg font-bold text-primary">Prestazioni</h2>
          <span class="text-sm text-muted">
            {{ numeroPrenotate }} su {{ prestazioni.length }} prenotate
          </span>
        </div>

        <UTable :data="prestazioni" :columns="colonne">
          <template #codice_prestazione-cell="{ row }">
            <span class="font-semibold">{{ row.original.codice_prestazione }}</span>
          </template>
          <template #azioni-cell="{ row }">
            <div class="flex items-center justify-end gap-2">
              <UButton
                v-if="!row.original.prenotata"
                label="Prenota"
                size="sm"
                @click="apriModale(row.original)"
              />
              <template v-else>
                <UBadge label="Prenotata" color="success" variant="subtle" />
                <UButton
                  label="Elimina"
                  size="sm"
                  color="error"
                  variant="ghost"
                  @click="eliminaPrenotazione(row.original)"
                />
              </template>
            </div>
          </template>
          <template #empty>Questa ricetta non contiene prestazioni.</template>
        </UTable>
      </UCard>
    </template>

    <UModal
      v-model:open="modaleAperta"
      title="Scegli un orario"
      :description="
        prestazioneScelta
          ? `${prestazioneScelta.codice_prestazione} - ${prestazioneScelta.descrizione}`
          : ''
      "
    >
      <template #body>
        <p v-if="caricamentoSlot" class="text-muted">Caricamento degli orari...</p>

        <p v-else-if="!slotLiberi.length" class="text-muted">
          Al momento non ci sono orari liberi per questa prestazione.
        </p>

        <div v-else class="space-y-5">
          <div v-for="[giorno, slots] in slotPerGiorno" :key="giorno">
            <p class="mb-2 font-semibold capitalize text-highlighted">
              {{ formatGiorno(giorno) }} {{ formatData(giorno) }}
            </p>
            <div class="grid grid-cols-2 gap-2 sm:grid-cols-4">
              <UButton
                v-for="slot in slots"
                :key="slot.id"
                :label="`${formatOra(slot.data_inizio_slot)} - ${formatOra(slot.data_fine_slot)}`"
                block
                :variant="slotScelto?.id === slot.id ? 'solid' : 'outline'"
                @click="slotScelto = slot"
              />
            </div>
          </div>

          <UFormField label="Note (facoltative)">
            <UTextarea v-model="notePaziente" :maxlength="255" :rows="3" class="w-full" />
          </UFormField>
        </div>
      </template>

      <template #footer>
        <div class="flex w-full justify-end gap-2">
          <UButton label="Annulla" color="neutral" variant="ghost" @click="modaleAperta = false" />
          <UButton
            label="Conferma prenotazione"
            :disabled="!slotScelto"
            loading-auto
            @click="confermaPrenotazione"
          />
        </div>
      </template>
    </UModal>
  </div>
</template>
