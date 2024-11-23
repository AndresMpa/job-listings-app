<script setup lang="ts">
const { setLocale } = useI18n();
</script>

<template>
  <div>
    <div>
      <button @click="setLocale('en')">en</button>
      <button @click="setLocale('fr')">fr</button>
      <p>{{ $t("welcome") }}</p>
    </div>
  </div>
</template>
