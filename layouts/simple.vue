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

.rotate-enter-active,
.rotate-leave-active {
  transition: all 0.4s;
}
.rotate-enter-from,
.rotate-leave-to {
  opacity: 0;
  transform: rotate3d(1, 1, 1, 15deg);
}
</style>
