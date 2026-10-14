<script setup lang="ts">
import { getLocalTimeZone, today } from '@internationalized/date'

const toast = useToast()
const api = useApi()

const authCookie = useCookie<any>('auth_user')
const pazienteId = authCookie.value?.id ?? null
const nomePaziente = authCookie.value?.nome || authCookie.value?.username || ''

const prenotazioneCookie = useCookie<{ id_ricetta: number; id_paziente: number | null }>(
  'prenotazione_prestazione'
)
const resocontoCookie = useCookie<{ id_prenotazione: number }>('resoconto_prenotazione')

const ricette = ref<any[]>([])
const prenotazioni = ref<any[]>([])
const medici = ref<any[]>([])
const prestazioni = ref<any[]>([])

const colonneRicette = [
  { accessorKey: 'nre', header: 'Numero ricetta' },
  { accessorKey: 'nome_medico', header: 'Medico' },
  { accessorKey: 'data_emissione', header: 'Emissione' },
  { accessorKey: 'data_scadenza', header: 'Scadenza' },
  { id: 'azioni', header: '' }
]

const colonnePrenotazioni = [
  { accessorKey: 'data_inizio_slot', header: 'Data' },
  { id: 'orario', header: 'Orario' },
  { accessorKey: 'descrizione', header: 'Prestazione' },
  { id: 'azioni', header: '' }
]

const prossimoAppuntamento = computed(() => {
  const adesso = Date.now()
  return prenotazioni.value
    .filter((p) => new Date(p.data_inizio_slot).getTime() > adesso)
    .sort((a, b) => a.data_inizio_slot.localeCompare(b.data_inizio_slot))[0]
})

// le date arrivano come "YYYY-MM-DD", basta confrontare le stringhe
const oggi = today(getLocalTimeZone()).toString()
const isScaduta = (data: string | null) => !!data && data < oggi

// modale nuova ricetta
const modaleAperta = ref(false)
const nre = ref('')
const dataEmissione = shallowRef<any>(today(getLocalTimeZone()))
const dataScadenza = shallowRef<any>(today(getLocalTimeZone()))
const medicoScelto = ref<any>(null)
const prestazioniScelte = ref<any[]>([])
const ricercaMedico = ref('')
const ricercaPrestazione = ref('')
const errori = reactive({ nre: '', medico: '' })

// scadenza max un anno dopo l'emissione
const maxScadenza = computed(() => dataEmissione.value.add({ years: 1 }))

watch(dataEmissione, () => {
  if (dataScadenza.value.compare(maxScadenza.value) > 0) dataScadenza.value = maxScadenza.value
})

watch(nre, (valore) => {
  const formattato = formattaNre(valore)
  if (formattato !== valore) nre.value = formattato
  errori.nre = ''
})

// cerca solo da 3 caratteri in su
function cerca(lista: any[], testo: string, campi: string[]) {
  const query = testo.trim().toLowerCase()
  if (query.length < 3) return []
  return lista.filter((item) => campi.some((campo) => item[campo]?.toLowerCase().includes(query)))
}

const mediciTrovati = computed(() =>
  cerca(medici.value, ricercaMedico.value, ['nome', 'cognome', 'specializzazione'])
)
const prestazioniTrovate = computed(() =>
  cerca(prestazioni.value, ricercaPrestazione.value, ['codice_prestazione', 'descrizione'])
)

const isAggiunta = (prestazione: any) =>
  prestazioniScelte.value.some((p) => p.id === prestazione.id)

function scegliMedico(medico: any) {
  medicoScelto.value = medico
  ricercaMedico.value = ''
  errori.medico = ''
}

function aggiungiPrestazione(prestazione: any) {
  if (!isAggiunta(prestazione)) prestazioniScelte.value.push(prestazione)
}

function rimuoviPrestazione(id: number) {
  prestazioniScelte.value = prestazioniScelte.value.filter((p) => p.id !== id)
}

function apriModale() {
  nre.value = ''
  dataEmissione.value = today(getLocalTimeZone())
  dataScadenza.value = today(getLocalTimeZone())
  medicoScelto.value = null
  prestazioniScelte.value = []
  ricercaMedico.value = ''
  ricercaPrestazione.value = ''
  errori.nre = ''
  errori.medico = ''
  modaleAperta.value = true
}

async function salvaRicetta() {
  const codiceNre = nre.value.replace(' ', '')
  if (codiceNre.length !== 15) errori.nre = 'Il numero di ricetta deve avere 15 caratteri'
  if (!medicoScelto.value) errori.medico = 'Seleziona il medico che ha emesso la ricetta'
  if (errori.nre || errori.medico) return

  if (dataScadenza.value.compare(maxScadenza.value) > 0) {
    toast.add({ title: 'La scadenza non può superare un anno dalla emissione', color: 'warning' })
    return
  }

  try {
    const ricetta: any = await api('/ricette/', {
      method: 'POST',
      body: {
        nre: codiceNre,
        id_medico: medicoScelto.value.id,
        data_emissione: dataEmissione.value.toString(),
        data_scadenza: dataScadenza.value.toString(),
        id_paziente: pazienteId
      }
    })
    // poi aggiungo le prestazioni alla ricetta appena creata
    await Promise.all(
      prestazioniScelte.value.map((prestazione) =>
        api('/ricetta-prestazione/', {
          method: 'POST',
          body: { id_ricetta: ricetta.id, id_prestazione: prestazione.id }
        })
      )
    )
    toast.add({ title: 'Ricetta salvata', color: 'success' })
    modaleAperta.value = false
  } catch (err: any) {
    console.error(err)
    toast.add({
      title: 'Impossibile salvare la ricetta',
      description: typeof err?.data?.detail === 'string' ? err.data.detail : undefined,
      color: 'error'
    })
  }
  await caricaRicette()
}

function vaiAPrenotazione(ricetta: any) {
  prenotazioneCookie.value = { id_ricetta: ricetta.id, id_paziente: pazienteId }
  navigateTo('/prenotazione_prestazione')
}

function vaiAResoconto(prenotazione: any) {
  resocontoCookie.value = { id_prenotazione: prenotazione.id }
  navigateTo('/resoconto_prenotazione')
}

async function caricaRicette() {
  try {
    ricette.value = await api(`/ricette/paziente/${pazienteId}`)
  } catch (err) {
    console.error(err)
  }
}

async function caricaDati() {
  try {
    const [listaPrenotazioni, listaMedici, listaPrestazioni] = await Promise.all([
      api<any[]>(`/prenotazioni/paziente/${pazienteId}`),
      api<any[]>('/medici/'),
      api<any[]>('/prestazioni/'),
      caricaRicette()
    ])
    prenotazioni.value = listaPrenotazioni
    medici.value = listaMedici
    prestazioni.value = listaPrestazioni
  } catch (err) {
    console.error(err)
  }
}

await caricaDati()
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-highlighted">Ciao {{ nomePaziente }}!</h1>
      <p class="text-muted">Qui trovi le tue ricette e le visite che hai prenotato.</p>
    </div>

    <UAlert
      v-if="prossimoAppuntamento"
      icon="i-lucide-calendar-clock"
      color="primary"
      variant="subtle"
      title="Prossimo appuntamento"
      :description="`${formatGiorno(prossimoAppuntamento.data_inizio_slot)} ${formatData(prossimoAppuntamento.data_inizio_slot)} alle ${formatOra(prossimoAppuntamento.data_inizio_slot)} - ${prossimoAppuntamento.descrizione}`"
    />

    <UCard>
      <div class="mb-2 flex flex-wrap items-center justify-between gap-2">
        <h2 class="text-lg font-bold text-primary">Le mie ricette</h2>
        <UButton label="Aggiungi ricetta" icon="i-lucide-plus" @click="apriModale" />
      </div>

      <UTable :data="ricette" :columns="colonneRicette">
        <template #nre-cell="{ row }">
          <span class="font-mono">{{ formattaNre(row.original.nre) }}</span>
        </template>
        <template #nome_medico-cell="{ row }">
          {{ row.original.nome_medico ?? '-' }}
        </template>
        <template #data_emissione-cell="{ row }">
          {{ formatData(row.original.data_emissione) }}
        </template>
        <template #data_scadenza-cell="{ row }">
          {{ formatData(row.original.data_scadenza) }}
          <UBadge
            v-if="isScaduta(row.original.data_scadenza)"
            label="Scaduta"
            color="error"
            variant="subtle"
            size="sm"
            class="ml-1"
          />
        </template>
        <template #azioni-cell="{ row }">
          <div class="text-right">
            <UButton
              v-if="!isScaduta(row.original.data_scadenza)"
              label="Prenota"
              size="sm"
              variant="soft"
              @click="vaiAPrenotazione(row.original)"
            />
          </div>
        </template>
        <template #empty>
          Non hai ancora inserito nessuna ricetta. Clicca su "Aggiungi ricetta" per iniziare.
        </template>
      </UTable>
    </UCard>

    <UCard>
      <h2 class="mb-2 text-lg font-bold text-primary">Le mie prenotazioni</h2>

      <UTable :data="prenotazioni" :columns="colonnePrenotazioni">
        <template #data_inizio_slot-cell="{ row }">
          {{ formatData(row.original.data_inizio_slot) }}
        </template>
        <template #orario-cell="{ row }">
          {{ formatOra(row.original.data_inizio_slot) }} -
          {{ formatOra(row.original.data_fine_slot) }}
        </template>
        <template #descrizione-cell="{ row }">
          <span class="font-semibold">{{ row.original.codice_prestazione }}</span>
          - {{ row.original.descrizione }}
        </template>
        <template #azioni-cell="{ row }">
          <div class="text-right">
            <UButton
              label="Resoconto"
              icon="i-lucide-file-text"
              size="sm"
              color="neutral"
              variant="outline"
              @click="vaiAResoconto(row.original)"
            />
          </div>
        </template>
        <template #empty>Non hai ancora prenotato nessuna prestazione.</template>
      </UTable>
    </UCard>

    <UModal
      v-model:open="modaleAperta"
      title="Nuova ricetta"
      :ui="{ content: 'w-full sm:max-w-2xl' }"
    >
      <template #body>
        <div class="space-y-4">
          <UFormField
            label="Numero di ricetta (NRE)"
            help="I 15 caratteri scritti sul promemoria della ricetta."
            :error="errori.nre"
            required
          >
            <UInput
              v-model="nre"
              placeholder="XXXXX XXXXXXXXXX"
              maxlength="16"
              class="w-full"
              :ui="{ base: 'font-mono tracking-wider' }"
            />
          </UFormField>

          <div class="grid gap-4 sm:grid-cols-2">
            <UFormField label="Data di emissione" required>
              <UInputDate v-model="dataEmissione" class="w-full" />
            </UFormField>
            <UFormField label="Data di scadenza" help="Al massimo un anno dopo l'emissione.">
              <UInputDate v-model="dataScadenza" :max-value="maxScadenza" class="w-full" />
            </UFormField>
          </div>

          <UFormField label="Medico" :error="errori.medico" required>
            <div
              v-if="medicoScelto"
              class="flex items-center justify-between gap-3 rounded-lg bg-primary/10 px-3 py-2"
            >
              <div>
                <p class="font-semibold">{{ medicoScelto.cognome }} {{ medicoScelto.nome }}</p>
                <p class="text-sm text-muted">{{ medicoScelto.specializzazione ?? '-' }}</p>
              </div>
              <UButton
                label="Cambia"
                size="sm"
                color="neutral"
                variant="ghost"
                @click="medicoScelto = null"
              />
            </div>
            <template v-else>
              <UInput
                v-model="ricercaMedico"
                icon="i-lucide-search"
                placeholder="Cerca per nome, cognome o specializzazione"
                class="w-full"
              />
              <ul
                v-if="mediciTrovati.length"
                class="mt-2 max-h-48 divide-y divide-default overflow-y-auto rounded-lg border border-default"
              >
                <li
                  v-for="medico in mediciTrovati"
                  :key="medico.id"
                  class="flex items-center justify-between gap-3 px-3 py-2"
                >
                  <div>
                    <p class="text-sm font-semibold">{{ medico.cognome }} {{ medico.nome }}</p>
                    <p class="text-xs text-muted">{{ medico.specializzazione ?? '-' }}</p>
                  </div>
                  <UButton label="Scegli" size="xs" variant="soft" @click="scegliMedico(medico)" />
                </li>
              </ul>
              <p v-else-if="ricercaMedico.trim().length >= 3" class="mt-2 text-sm text-muted">
                Nessun medico trovato.
              </p>
            </template>
          </UFormField>

          <UFormField label="Prestazioni prescritte">
            <UInput
              v-model="ricercaPrestazione"
              icon="i-lucide-search"
              placeholder="Cerca per codice o descrizione (almeno 3 caratteri)"
              class="w-full"
            />
            <ul
              v-if="prestazioniTrovate.length"
              class="mt-2 max-h-60 divide-y divide-default overflow-y-auto rounded-lg border border-default"
            >
              <li
                v-for="prestazione in prestazioniTrovate"
                :key="prestazione.id"
                class="flex items-center justify-between gap-3 px-3 py-2"
              >
                <p class="text-sm">
                  <span class="font-semibold">{{ prestazione.codice_prestazione }}</span>
                  - {{ prestazione.descrizione }}
                </p>
                <UButton
                  :label="isAggiunta(prestazione) ? 'Aggiunta' : 'Aggiungi'"
                  :disabled="isAggiunta(prestazione)"
                  size="xs"
                  variant="soft"
                  @click="aggiungiPrestazione(prestazione)"
                />
              </li>
            </ul>
            <p v-else-if="ricercaPrestazione.trim().length >= 3" class="mt-2 text-sm text-muted">
              Nessuna prestazione trovata.
            </p>

            <div v-if="prestazioniScelte.length" class="mt-3">
              <p class="mb-1 text-sm text-muted">
                Aggiunte alla ricetta ({{ prestazioniScelte.length }}):
              </p>
              <div class="flex flex-wrap gap-2">
                <UBadge
                  v-for="prestazione in prestazioniScelte"
                  :key="prestazione.id"
                  variant="subtle"
                  class="gap-1"
                >
                  {{ prestazione.codice_prestazione }} - {{ prestazione.descrizione }}
                  <UButton
                    icon="i-lucide-x"
                    size="xs"
                    color="neutral"
                    variant="link"
                    class="p-0"
                    :aria-label="`Rimuovi ${prestazione.codice_prestazione}`"
                    @click="rimuoviPrestazione(prestazione.id)"
                  />
                </UBadge>
              </div>
            </div>
          </UFormField>
        </div>
      </template>

      <template #footer>
        <div class="flex w-full justify-end gap-2">
          <UButton label="Annulla" color="neutral" variant="ghost" @click="modaleAperta = false" />
          <UButton label="Salva ricetta" loading-auto @click="salvaRicetta" />
        </div>
      </template>
    </UModal>
  </div>
</template>
