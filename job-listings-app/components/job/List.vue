<script setup lang="ts">
import type { Job } from "@/lib/types";

const props = defineProps<{
  jobData: Job[];
  selectedTags?: string[];
}>();

const emit = defineEmits<{ handleTag: [tag: string] }>();

const handleTag = (value: string) => emit("handleTag", value);

// A job must carry every selected tag (source or keyword chip) to show up.
const visibleJobs = computed(() => {
  const tags = props.selectedTags ?? [];
  if (tags.length === 0) return props.jobData;
  return props.jobData.filter((job) => {
    const chips = [job.source, ...job.tags];
    return tags.every((tag) => chips.includes(tag));
  });
});
</script>

<template>
  <p v-if="visibleJobs.length === 0" class="text-center text-primary-foreground text-lg my-12">
    No listings match the selected filters.
  </p>
  <ul class="list-none my-6" v-for="job in visibleJobs" :key="job.id">
    <JobItem :job="job" :tags="selectedTags" @add-tag="handleTag" />
  </ul>
</template>
