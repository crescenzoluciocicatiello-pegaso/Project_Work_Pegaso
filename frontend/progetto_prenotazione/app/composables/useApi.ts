// $fetch con già l'indirizzo del backend
export const useApi = () => $fetch.create({ baseURL: useRuntimeConfig().public.apiBase })
