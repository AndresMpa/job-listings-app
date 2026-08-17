<script setup lang="ts">
useHead({
  titleTemplate: "Job Listing App %s",
  meta: [
    { name: "description", content: "Simple job listing app" },
  ],
  htmlAttrs: {
    lang: "en",
  },
  link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
});
</script>

<template>
  <div>
    <slot />
  </div>
</template>

<style>
.page-enter-active,
.page-leave-active {
  transition: all 0.4s;
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
  filter: blur(1rem);
}
</style>
