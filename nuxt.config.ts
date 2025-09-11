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
  i18n: {
    strategy: "prefix_except_default",
    defaultLocale: "en",
    locales: [
      {
        code: "en",
        iso: "en-US",
        name: "English",
        file: "en.json",
      },
      {
        code: "es",
        iso: "es-ES",
        name: "Español",
        file: "es.json",
      },
    ],
    langDir: "locales/",
  },
  routeRules: {
    "/": { prerender: true, redirect: "/jobs" },
    "/jobs": { ssr: false },
    "/about": { ssr: true, redirect: "/jobs" },
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
