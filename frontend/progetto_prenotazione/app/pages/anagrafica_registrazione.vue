<script setup lang="ts">
import * as z from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'
import { getLocalTimeZone, today, type DateValue } from '@internationalized/date'

definePageMeta({ layout: 'auth' })

const toast = useToast()
const api = useApi()

// la data di nascita sta fuori da state: dentro reactive() UInputDate non funzionava
const dataNascita = shallowRef<DateValue>()
const oggi = today(getLocalTimeZone())
const validaDataNascita = () =>
  dataNascita.value ? [] : [{ name: 'dataNascita', message: 'Campo obbligatorio' }]

const schema = z
  .object({
    username: z
      .string()
      .min(5, 'Almeno 5 caratteri')
      .transform((valore) => valore.toLowerCase()),
    email: z.email('Email non valida'),
    password: z.string().min(8, 'Almeno 8 caratteri'),
    confirmPassword: z.string(),
    nome: z.string().min(1, 'Campo obbligatorio'),
    cognome: z.string().min(1, 'Campo obbligatorio'),
    sesso: z.enum(['M', 'F']),
    telefono: z.string().regex(/^\+?[0-9 \-().]{6,}$/, 'Numero di telefono non valido'),
    comuneDiNascita: z.string().min(1, 'Campo obbligatorio'),
    codiceFiscale: z
      .string()
      .min(11, 'Codice fiscale non valido')
      .max(16, 'Codice fiscale non valido')
      .transform((valore) => valore.toUpperCase())
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Le password non coincidono',
    path: ['confirmPassword']
  })

type Schema = z.output<typeof schema>

const state = reactive<Partial<Schema>>({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  nome: '',
  cognome: '',
  sesso: 'M',
  telefono: '',
  comuneDiNascita: '',
  codiceFiscale: ''
})

async function onSubmit(event: FormSubmitEvent<Schema>) {
  const { data } = event
  try {
    await api('/utenti_pazienti/', {
      method: 'POST',
      body: {
        username: data.username,
        email: data.email,
        nome: data.nome,
        cognome: data.cognome,
        sesso: data.sesso,
        telefono: data.telefono,
        data_nascita: dataNascita.value?.toString(),
        comune_nascita: data.comuneDiNascita,
        codice_fiscale: data.codiceFiscale,
        password: data.password
      }
    })
    toast.add({ title: 'Registrazione completata, ora puoi accedere', color: 'success' })
    await navigateTo('/')
  } catch (err: any) {
    console.error(err)
    toast.add({
      title: 'Registrazione non riuscita',
      // con il 422 detail è una lista, la mostro solo se è un messaggio
      description:
        typeof err?.data?.detail === 'string' ? err.data.detail : 'Controlla i dati e riprova.',
      color: 'error'
    })
  }
}
</script>

<template>
  <UCard class="w-full max-w-2xl">
    <h1 class="text-xl font-bold text-highlighted">Registrazione</h1>
    <p class="mb-6 text-sm text-muted">Compila i campi per creare il tuo account.</p>

    <UForm
      :schema="schema"
      :state="state"
      :validate="validaDataNascita"
      class="space-y-6"
      @submit="onSubmit"
    >
      <div>
        <h2 class="mb-3 font-semibold text-primary">Dati di accesso</h2>
        <div class="grid gap-4 sm:grid-cols-2">
          <UFormField name="username" label="Username" required>
            <UInput v-model="state.username" placeholder="mario.rossi" class="w-full" />
          </UFormField>

          <UFormField name="email" label="Email" required>
            <UInput
              v-model="state.email"
              type="email"
              placeholder="mario.rossi@email.it"
              class="w-full"
            />
          </UFormField>

          <UFormField name="password" label="Password" required>
            <UInput v-model="state.password" type="password" class="w-full" />
          </UFormField>

          <UFormField name="confirmPassword" label="Ripeti la password" required>
            <UInput v-model="state.confirmPassword" type="password" class="w-full" />
          </UFormField>
        </div>
      </div>

      <div>
        <h2 class="mb-3 font-semibold text-primary">Dati personali</h2>
        <div class="grid gap-4 sm:grid-cols-2">
          <UFormField name="nome" label="Nome" required>
            <UInput v-model="state.nome" class="w-full" />
          </UFormField>

          <UFormField name="cognome" label="Cognome" required>
            <UInput v-model="state.cognome" class="w-full" />
          </UFormField>

          <UFormField name="sesso" label="Sesso" required>
            <USelect v-model="state.sesso" :items="['M', 'F']" class="w-full" />
          </UFormField>

          <UFormField name="dataNascita" label="Data di nascita" required>
            <UInputDate v-model="dataNascita" :max-value="oggi" class="w-full" />
          </UFormField>

          <UFormField name="comuneDiNascita" label="Comune di nascita" required>
            <UInput v-model="state.comuneDiNascita" class="w-full" />
          </UFormField>

          <UFormField name="codiceFiscale" label="Codice fiscale" required>
            <UInput
              v-model="state.codiceFiscale"
              maxlength="16"
              class="w-full"
              :ui="{ base: 'uppercase' }"
            />
          </UFormField>

          <UFormField name="telefono" label="Telefono" required>
            <UInput v-model="state.telefono" type="tel" class="w-full" />
          </UFormField>
        </div>
      </div>

      <UButton type="submit" label="Crea account" block loading-auto />

      <p class="text-center text-sm text-muted">
        Hai già un account?
        <NuxtLink to="/" class="font-semibold text-primary hover:underline">Accedi</NuxtLink>
      </p>
    </UForm>
  </UCard>
</template>
