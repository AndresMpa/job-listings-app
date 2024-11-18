// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2024-04-03",
  devtools: { enabled: true },
  $test: { logLevel: "silent" },
  $development: { logLevel: "warning" },
  $production: { logLevel: "error" },
  $env: {
    staging: { logLevel: "debug" },
  },
});
