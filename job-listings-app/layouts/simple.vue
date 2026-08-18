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
      <div>
        <NuxtLink to="/settings" class="text-primary font-bold hover:underline">Settings</NuxtLink>
      </div>
      <div>
        <UtilLanguageSwitcher />
      </div>
      <div>
        <UtilThemeSwitcher />
      </div>
    </AppHoverMenu>
    <slot />
  </div>
</template>
