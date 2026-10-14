<template>
  <div class="relative flex min-h-screen flex-col items-center justify-center px-4 py-10">
    <AppTemaButton class="absolute top-4 right-4" />
    <AppLogo class="mb-6" />
    <slot />
    <p class="mt-8 text-center text-sm text-muted">
      Rete Sanitaria - Servizio di prenotazione delle prestazioni sanitarie
    </p>
  </div>
</template>
