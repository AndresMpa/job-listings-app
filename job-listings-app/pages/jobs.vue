<script setup lang="ts">
import type { Job, ProfileSettings } from "@/lib/types";

definePageMeta({
  layout: "simple",
  pageTransition: {
    name: "rotate",
  },
});

// Multiple people can search at once (see job-search-automation/profiles/);
// this lets the frontend show one person's matches at a time, or everyone's.
const { data: profiles } = await useFetch<ProfileSettings[]>("/api/profiles");
const selectedProfile = ref<string>(""); // "" = every profile

const { data } = await useFetch<Job[]>("/api/jobs", {
  query: computed(() => (selectedProfile.value ? { profile: selectedProfile.value } : {})),
});

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
    <div v-if="profiles && profiles.length > 1" class="absolute right-4 top-4 z-10">
      <label class="flex items-center gap-2 text-sm text-primary-foreground">
        Profile
        <select
          v-model="selectedProfile"
          class="rounded border border-gray-300 bg-primary-foreground px-2 py-1 text-foreground"
        >
          <option value="">All profiles</option>
          <option v-for="p in profiles" :key="p.name" :value="p.name">{{ p.name }}</option>
        </select>
      </label>
    </div>
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