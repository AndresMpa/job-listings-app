<script setup lang="ts">
useHead({
  titleTemplate: "Job Listing App %s",
});
</script>

<template>
  <div class="bg-primary sm:bg-theme-desktop bg-theme-mobile">
    <AppHoverMenu>
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

<style>
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
