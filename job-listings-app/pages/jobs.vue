<script setup lang="ts">
import { Button } from "@/components/ui/button";
import type { Job, ProfileSettings } from "@/lib/types";

definePageMeta({
  layout: "simple",
  pageTransition: { name: "rotate" },
});

const { data: profiles } = await useFetch<ProfileSettings[]>("/api/profiles");
const selectedProfile = ref<string>("");

const { data, error, refresh } = await useFetch<Job[]>("/api/jobs", {
  query: computed(() => (selectedProfile.value ? { profile: selectedProfile.value } : {})),
});

const selectedTags = ref<string[]>([]);
const handleTag = (tag: string) => {
  const index = selectedTags.value.indexOf(tag);
  index === -1 ? selectedTags.value.push(tag) : selectedTags.value.splice(index, 1);
};
const clearTags = () => (selectedTags.value = []);

// useFetch surfaces backend failures via `error`, with the HTTP status on
// `.statusCode`. 503 = schema not initialized; anything else = real failure.
const schemaMissing = computed(() => error.value?.statusCode === 503);

const initializing = ref(false);
const initError = ref("");
async function initDatabase() {
  initializing.value = true;
  initError.value = "";
  try {
    await $fetch("/api/init-db", { method: "POST" });
    await refresh();
  } catch {
    initError.value = "Could not initialize the database. Please try again.";
  } finally {
    initializing.value = false;
  }
}

const running = ref(false);
const runError = ref("");
async function startSearch() {
  running.value = true;
  runError.value = "";
  try {
    await $fetch("/api/run", {
      method: "POST",
      query: selectedProfile.value ? { profile: selectedProfile.value } : {},
    });
    await refresh();
  } catch {
    runError.value = "Could not start the search. Please try again.";
  } finally {
    running.value = false;
  }
}
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

    <div v-if="selectedTags.length !== 0" class="transition-opacity duration-500 ease-in-out">
      <JobFilter @remove-tag="handleTag" @clear-tags="clearTags" :selected-tags="selectedTags" />
    </div>

    <!-- Results -->
    <div v-if="data && data.length > 0" :class="selectedTags.length !== 0 ? 'mt-11' : 'mt-24'">
      <JobList :job-data="data" :selected-tags="selectedTags" @handle-tag="handleTag" />
    </div>

    <!-- Empty state: no schema yet -->
    <div v-else-if="schemaMissing" class="flex flex-col items-center justify-center gap-3 mt-24">
      <p class="text-sm text-primary-foreground">The database hasn't been set up yet.</p>
      <Button size="lg" :disabled="initializing" @click="initDatabase">
        {{ initializing ? "Setting up…" : "Initialize database" }}
      </Button>
      <p v-if="initError" class="text-sm text-destructive">{{ initError }}</p>
    </div>

    <!-- Empty state: schema ready, no results yet -->
    <div v-else-if="data" class="flex flex-col items-center justify-center gap-3 mt-24">
      <Button size="lg" :disabled="running" @click="startSearch">
        {{ running ? "Searching…" : "Start to search" }}
      </Button>
      <p v-if="runError" class="text-sm text-destructive">{{ runError }}</p>
    </div>
  </div>
</template>
