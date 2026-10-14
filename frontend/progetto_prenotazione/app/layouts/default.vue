<script setup lang="ts">
const authCookie = useCookie<any>('auth_user')

const nomeUtente = computed(() =>
  authCookie.value?.nome
    ? `${authCookie.value.nome} ${authCookie.value.cognome ?? ''}`
    : authCookie.value?.username
)

function esci() {
  authCookie.value = null
  navigateTo('/')
}
</script>

<template>
  <div class="flex min-h-screen flex-col">
    <header
      class="border-t-4 border-b border-t-primary border-b-default bg-default shadow-sm print:hidden"
    >
      <div class="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3">
        <NuxtLink to="/dashboard_paziente">
          <AppLogo />
        </NuxtLink>
        <div class="flex items-center gap-3">
          <span class="hidden text-sm text-muted sm:inline">{{ nomeUtente }}</span>
          <AppTemaButton />
          <UButton
            label="Esci"
            icon="i-lucide-log-out"
            color="neutral"
            variant="outline"
            size="sm"
            @click="esci"
          />
        </div>
      </div>
    </header>

    <main class="mx-auto w-full max-w-5xl flex-1 px-4 py-8">
      <slot />
    </main>

    <footer class="py-6 text-center text-sm text-muted print:hidden">
      Rete Sanitaria - Servizio di prenotazione delle prestazioni sanitarie
    </footer>
  </div>
</template>
