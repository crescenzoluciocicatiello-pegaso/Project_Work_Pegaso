<script setup lang="ts">
const colorMode = useColorMode()

function cambiaTema() {
  colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'
}
</script>

<template>
  <UButton color="neutral" variant="ghost" square aria-label="Cambia tema" @click="cambiaTema">
    <!-- luna col tema chiaro, sole col tema scuro -->
    <UIcon name="i-lucide-moon" class="size-5 dark:hidden" />
    <UIcon name="i-lucide-sun" class="hidden size-5 dark:inline-block" />
  </UButton>
</template>
