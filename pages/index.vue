<script setup lang="ts">
import type { Job } from "@/lib/types";

definePageMeta({
  layout: "simple",
});

const { data } = await useFetch<Job[]>("/api/jobs");
</script>

<template>
  <div>
    <div class="relative h-40 pt-32">
      <JobFilter />
      <div v-if="data">
        <JobList :job-data="data" />
      </div>
    </div>
  </div>
</template>
