<script setup lang="ts">
import type { Job } from "@/lib/types";

definePageMeta({
  layout: "simple",
  pageTransition: {
    name: "rotate",
  },
});

const { data } = await useFetch<Job[]>("/api/jobs");

const selectedTags = ref<string[]>([]);

const handleTag = (tag: string) => {
  const index = selectedTags.value.indexOf(tag);

  index === -1
    ? selectedTags.value.push(tag)
    : selectedTags.value.splice(index, 1);
};

const clearTags = () => (selectedTags.value = []);
</script>

<template>
  <div class="relative h-40 pt-32">
    <div
      v-if="selectedTags.length !== 0"
      class="transition-opacity duration-500 ease-in-out"
    >
      <JobFilter
        @remove-tag="handleTag"
        @clear-tags="clearTags"
        :selected-tags="selectedTags"
      />
    </div>
    <div v-if="data" :class="selectedTags.length !== 0 ? 'mt-11' : 'mt-24'">
      <JobList
        :job-data="data"
        :selected-tags="selectedTags"
        @handle-tag="handleTag"
      />
    </div>
  </div>
</template>