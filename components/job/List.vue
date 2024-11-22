<script setup lang="ts">
import type { Job } from "@/lib/types";

const props = defineProps({
  jobData: {
    type: Array<Job>,
    required: true,
  },
});
</script>

<template>
  <li
    class="list-none my-6 mt-10"
    v-for="(job, index) in props.jobData"
    :index="index"
    :key="job.id"
  >
    <JobItem :job="job" />
  </li>
</template>
