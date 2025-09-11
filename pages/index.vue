<script setup lang="ts">
import { useI18n } from "vue-i18n";
const { t } = useI18n();

definePageMeta({
  pageTransition: {
    name: "rotate",
  },
});
</script>

<template>
  <h1>
    {{ t("title") }}
  </h1>
</template>
