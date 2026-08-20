<script setup lang="ts">
import { ref } from 'vue'

useHead({
  titleTemplate: "Job Listing App %s",
  meta: [{ name: "description", content: "Simple job listing app" }],
  htmlAttrs: {
    lang: "en",
  },
  link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
});

const open = ref(false)
</script>

<template>
  <SidebarProvider :open="open" @update:open="open = $event">
    <AppSidebar />
    <main class="mx-auto w-screen bg-primary sm:bg-theme-desktop bg-theme-mobile">
      <SidebarTrigger class="rounded text-primary-foreground"/>
      <slot />
    </main>
  </SidebarProvider>
</template>
