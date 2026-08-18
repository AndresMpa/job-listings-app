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
  <div class="bg-primary sm:bg-theme-desktop bg-theme-mobile">
    <AppHoverMenu>
      <h2>Navigation</h2>
      <div class="flex flex-col justify-start gap-y-2">
        <NuxtLink to="/" class="text-primary font-bold my-auto hover:underline">Home</NuxtLink>
        <NuxtLink to="/jobs" class="text-primary font-bold my-auto hover:underline">Jobs</NuxtLink>
        <NuxtLink to="/profiles" class="text-primary font-bold my-auto hover:underline">Profiles</NuxtLink>
        <NuxtLink to="/settings" class="text-primary font-bold my-auto hover:underline">Settings</NuxtLink>
      </div>
    </AppHoverMenu>
    <slot />
  </div>
</template>
