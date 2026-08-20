import type { Job } from "@/lib/types";

export function useJobsFeed(profile: Ref<string> | ComputedRef<string>) {
  const { data, error, refresh } = useFetch<Job[]>("/api/jobs", {
    query: computed(() => (profile.value ? { profile: profile.value } : {})),
  });

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
        query: profile.value ? { profile: profile.value } : {},
      });
      await refresh();
    } catch {
      runError.value = "Could not start the search. Please try again.";
    } finally {
      running.value = false;
    }
  }

  return {
    data,
    error,
    refresh,
    schemaMissing,
    initializing,
    initError,
    initDatabase,
    running,
    runError,
    startSearch,
  };
}
