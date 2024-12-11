<script setup lang="ts">
useHead({
  titleTemplate: "Job Listing App %s",
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
