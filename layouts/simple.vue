<script setup lang="ts">
useHead({
  titleTemplate: "Job Listing App %s",
});
</script>

<template>
  <div class="bg-primary md:bg-theme-desktop bg-theme-mobile">
    <div class="relative">
      <div class="absolute top-2 right-2">
        <AppHoverMenu />
      </div>
    </div>
    <slot />
  </div>
</template>
