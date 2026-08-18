// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2024-11-01",
  devtools: { enabled: true },

  modules: [
    "@nuxtjs/tailwindcss",
    "shadcn-nuxt",
    "@nuxtjs/color-mode",
    "@nuxtjs/i18n",
  ],

  components: [
    {
      path: '~/components/ui',
      pathPrefix: false,
      pattern: '**/*.vue',
    },
    {
      path: '~/components',
      pathPrefix: true,
    },
  ],

  shadcn: {
    prefix: '',
    componentDir: './components/ui'
  },

  i18n: {
    strategy: "prefix_except_default",
    defaultLocale: "en",
    locales: [
      { code: "en", iso: "en-US", name: "English", file: "en.json" },
      { code: "es", iso: "es-ES", name: "Español", file: "es.json" },
    ],
    langDir: "locales/",
  },

  routeRules: {
    "/": { prerender: true, redirect: "/home" },
    "/home": { ssr: true },
    "/profiles": { ssr: false },
    "/jobs": { ssr: false },
    "/jobs/**": { ssr: false },
    "/about": { ssr: true, redirect: "/jobs" },
    "/settings": { ssr: false },
  },

  runtimeConfig: {
    backendUrl: process.env.NUXT_BACKEND_URL || "http://localhost:8000",
  },

  typescript: {
    typeCheck: true,
  },

  colorMode: {
    classSuffix: "",
    preference: "dark",
    fallback: "dark",
  },
});
