<script setup lang="ts">
import * as z from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'

definePageMeta({ layout: 'auth' })

const toast = useToast()
const api = useApi()
const authCookie = useCookie('auth_user')

const schema = z.object({
  username: z
    .string()
    .min(5, 'Almeno 5 caratteri')
    .transform((valore) => valore.toLowerCase()),
  password: z.string().min(8, 'Almeno 8 caratteri')
})

type Schema = z.output<typeof schema>

const state = reactive({ username: '', password: '' })
const mostraPassword = ref(false)

// croci sullo sfondo
const croci = [
  { classe: 'top-[12%] left-[8%] size-14', durata: '7s' },
  { classe: 'top-[28%] right-[10%] size-10', durata: '9s' },
  { classe: 'bottom-[18%] left-[14%] size-12', durata: '8s' },
  { classe: 'bottom-[10%] right-[16%] size-16', durata: '10s' },
  { classe: 'top-[55%] left-[4%] size-8', durata: '6s' },
  { classe: 'top-[8%] right-[35%] size-8', durata: '11s' }
]

async function onSubmit(event: FormSubmitEvent<Schema>) {
  try {
    // il backend restituisce i dati del paziente, li tengo nel cookie
    authCookie.value = await api('/utenti_pazienti/login', {
      method: 'POST',
      body: { username: event.data.username, password: event.data.password }
    })
    await navigateTo('/dashboard_paziente')
  } catch (err: any) {
    console.error(err)
    toast.add({
      title: err?.statusCode === 401 ? 'Username o password errati' : 'Errore di connessione',
      color: 'error'
    })
  }
}
</script>

<template>
  <div class="w-full max-w-sm">
    <UIcon
      v-for="croce in croci"
      :key="croce.classe"
      name="i-lucide-cross"
      class="croce pointer-events-none fixed text-primary/20"
      :class="croce.classe"
      :style="{ animationDuration: croce.durata }"
    />

    <UCard class="relative w-full">
      <h1 class="text-xl font-bold text-highlighted">Accedi</h1>
      <p class="mb-6 text-sm text-muted">Entra per vedere le tue ricette e prenotare le visite.</p>

      <UForm :schema="schema" :state="state" class="space-y-4" @submit="onSubmit">
        <UFormField label="Username" name="username">
          <UInput v-model="state.username" class="w-full" />
        </UFormField>

        <UFormField label="Password" name="password">
          <UInput
            v-model="state.password"
            :type="mostraPassword ? 'text' : 'password'"
            class="w-full"
            :ui="{ trailing: 'pe-1' }"
          >
            <template #trailing>
              <UButton
                :icon="mostraPassword ? 'i-lucide-eye-off' : 'i-lucide-eye'"
                aria-label="Mostra password"
                color="neutral"
                variant="link"
                size="sm"
                @click="mostraPassword = !mostraPassword"
              />
            </template>
          </UInput>
        </UFormField>

        <UButton type="submit" label="Accedi" block loading-auto />
      </UForm>

      <p class="mt-6 text-center text-sm text-muted">
        Non hai un account?
        <NuxtLink to="/anagrafica_registrazione" class="font-semibold text-primary hover:underline">
          Registrati
        </NuxtLink>
      </p>
    </UCard>
  </div>
</template>

<style>
.croce {
  animation: fluttua 8s ease-in-out infinite alternate;
}

@keyframes fluttua {
  from {
    transform: translateY(0) rotate(0deg);
  }
  to {
    transform: translateY(-30px) rotate(25deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .croce {
    animation: none;
  }
}
</style>
