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
