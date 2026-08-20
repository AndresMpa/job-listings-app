<script setup lang="ts">
useHead({
  titleTemplate: "Job Listing App %s",
  meta: [{ name: "description", content: "Simple job listing app" }],
  htmlAttrs: {
    lang: "en",
  },
  link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
});
</script>

<template>
  <SidebarProvider class="min-h-svh">
    <AppSidebar />
    <SidebarInset>
      <header class="flex h-14 items-center gap-2 border-b px-4">
        <SidebarTrigger class="size-7 text-foreground hover:bg-accent hover:text-accent-foreground" />
      </header>
      <slot />
    </SidebarInset>
  </SidebarProvider>
</template>
