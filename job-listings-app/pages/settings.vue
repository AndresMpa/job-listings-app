<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AppSettings } from "@/lib/types";

definePageMeta({
  layout: "simple",
});

const { data: settings, refresh } = await useFetch<AppSettings>("/api/settings");

const saving = ref(false);
const saveError = ref("");
const saveOk = ref(false);

// Keyword/list fields are edited as one-item-per-line textareas.
const toLines = (arr: string[] | undefined) => (arr ?? []).join("\n");
const fromLines = (text: string) =>
  text
    .split("\n")
    .map((s) => s.trim())
    .filter(Boolean);

const form = reactive({
  profile: "",
  ollamaUrl: "",
  ollamaModel: "",
  ollamaTimeout: 300,
  keywordsTarget: "",
  keywordsExclude: "",
  keywordsSeniority: "",
  keywordsAi: "",
  keywordsTech: "",
  providers: {
    remoteok: true,
    remotive: true,
    weworkremotely: true,
    python_jobs: true,
    vuejobs: true,
    hackernews: true,
    arbeitnow: true,
  },
  wwrCategories: "",
  minScoreToKeep: 6,
  fitWeight: 0.4,
  incomeWeight: 0.6,
  outputDir: ".",
  csvFilename: "job_matches.csv",
  mdFilename: "job_matches.md",
  databaseUrl: "",
});

function loadForm(s: AppSettings) {
  form.profile = s.profile;
  form.ollamaUrl = s.ollama.url;
  form.ollamaModel = s.ollama.model;
  form.ollamaTimeout = s.ollama.timeout;
  form.keywordsTarget = toLines(s.keywords.target);
  form.keywordsExclude = toLines(s.keywords.exclude);
  form.keywordsSeniority = toLines(s.keywords.seniority);
  form.keywordsAi = toLines(s.keywords.ai);
  form.keywordsTech = toLines(s.keywords.tech);
  form.providers = { ...s.providers };
  form.wwrCategories = toLines(s.weworkremotely.categories);
  form.minScoreToKeep = s.scoring.min_score_to_keep;
  form.fitWeight = s.scoring.fit_weight;
  form.incomeWeight = s.scoring.income_weight;
  form.outputDir = s.output.dir;
  form.csvFilename = s.output.csv_filename;
  form.mdFilename = s.output.md_filename;
  form.databaseUrl = s.database.url;
}

watch(settings, (s) => s && loadForm(s), { immediate: true });

async function save() {
  saving.value = true;
  saveError.value = "";
  saveOk.value = false;

  const payload: AppSettings = {
    profile: form.profile,
    ollama: { url: form.ollamaUrl, model: form.ollamaModel, timeout: form.ollamaTimeout },
    keywords: {
      target: fromLines(form.keywordsTarget),
      exclude: fromLines(form.keywordsExclude),
      seniority: fromLines(form.keywordsSeniority),
      ai: fromLines(form.keywordsAi),
      tech: fromLines(form.keywordsTech),
    },
    providers: { ...form.providers },
    weworkremotely: { categories: fromLines(form.wwrCategories) },
    scoring: {
      min_score_to_keep: form.minScoreToKeep,
      fit_weight: form.fitWeight,
      income_weight: form.incomeWeight,
    },
    output: { dir: form.outputDir, csv_filename: form.csvFilename, md_filename: form.mdFilename },
    database: { url: form.databaseUrl },
  };

  try {
    await $fetch("/api/settings", { method: "PUT", body: payload });
    saveOk.value = true;
    await refresh();
  } catch (err: any) {
    saveError.value = err?.data?.statusMessage || "Could not save settings";
  } finally {
    saving.value = false;
  }
}

const providerLabels: Record<keyof AppSettings["providers"], string> = {
  remoteok: "RemoteOK",
  remotive: "Remotive",
  weworkremotely: "We Work Remotely",
  python_jobs: "Python.org Jobs",
  vuejobs: "VueJobs",
  hackernews: "Hacker News",
  arbeitnow: "Arbeitnow",
};
</script>

<template>
  <div class="relative pt-32 pb-20 max-w-3xl mx-auto px-4">
    <h1 class="text-3xl font-bold text-primary-foreground mb-8">Settings</h1>

    <div v-if="!settings" class="text-primary-foreground">Loading configuration…</div>

    <form v-else class="space-y-6" @submit.prevent="save">
      <Card class="bg-primary-foreground">
        <CardHeader><CardTitle>Candidate profile</CardTitle></CardHeader>
        <CardContent>
          <textarea
            v-model="form.profile"
            rows="6"
            class="w-full rounded border border-gray-300 p-2 font-mono text-sm"
          />
        </CardContent>
      </Card>

      <Card class="bg-primary-foreground">
        <CardHeader><CardTitle>Ollama</CardTitle></CardHeader>
        <CardContent class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <label class="flex flex-col gap-1 text-sm">
            URL (empty = auto-detect)
            <input v-model="form.ollamaUrl" class="rounded border border-gray-300 p-2" />
          </label>
          <label class="flex flex-col gap-1 text-sm">
            Model
            <input v-model="form.ollamaModel" class="rounded border border-gray-300 p-2" />
          </label>
          <label class="flex flex-col gap-1 text-sm">
            Timeout (seconds)
            <input v-model.number="form.ollamaTimeout" type="number" class="rounded border border-gray-300 p-2" />
          </label>
        </CardContent>
      </Card>

      <Card class="bg-primary-foreground">
        <CardHeader><CardTitle>Keywords (one per line)</CardTitle></CardHeader>
        <CardContent class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <label class="flex flex-col gap-1 text-sm">
            Target — at least one must match
            <textarea v-model="form.keywordsTarget" rows="6" class="rounded border border-gray-300 p-2 font-mono text-sm" />
          </label>
          <label class="flex flex-col gap-1 text-sm">
            Exclude — any match disqualifies
            <textarea v-model="form.keywordsExclude" rows="6" class="rounded border border-gray-300 p-2 font-mono text-sm" />
          </label>
          <label class="flex flex-col gap-1 text-sm">
            Seniority
            <textarea v-model="form.keywordsSeniority" rows="4" class="rounded border border-gray-300 p-2 font-mono text-sm" />
          </label>
          <label class="flex flex-col gap-1 text-sm">
            AI-related
            <textarea v-model="form.keywordsAi" rows="4" class="rounded border border-gray-300 p-2 font-mono text-sm" />
          </label>
          <label class="flex flex-col gap-1 text-sm md:col-span-2">
            Technical (must match at least one)
            <textarea v-model="form.keywordsTech" rows="4" class="rounded border border-gray-300 p-2 font-mono text-sm" />
          </label>
        </CardContent>
      </Card>

      <Card class="bg-primary-foreground">
        <CardHeader><CardTitle>Providers</CardTitle></CardHeader>
        <CardContent class="grid grid-cols-2 md:grid-cols-3 gap-3">
          <label
            v-for="(label, key) in providerLabels"
            :key="key"
            class="flex items-center gap-2 text-sm"
          >
            <input type="checkbox" v-model="form.providers[key]" />
            {{ label }}
          </label>
        </CardContent>
      </Card>

      <Card class="bg-primary-foreground">
        <CardHeader><CardTitle>We Work Remotely categories (one per line)</CardTitle></CardHeader>
        <CardContent>
          <textarea v-model="form.wwrCategories" rows="4" class="w-full rounded border border-gray-300 p-2 font-mono text-sm" />
        </CardContent>
      </Card>

      <Card class="bg-primary-foreground">
        <CardHeader><CardTitle>Scoring</CardTitle></CardHeader>
        <CardContent class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <label class="flex flex-col gap-1 text-sm">
            Minimum score to keep (0-10)
            <input v-model.number="form.minScoreToKeep" type="number" min="0" max="10" class="rounded border border-gray-300 p-2" />
          </label>
          <label class="flex flex-col gap-1 text-sm">
            Fit weight
            <input v-model.number="form.fitWeight" type="number" step="0.1" min="0" max="1" class="rounded border border-gray-300 p-2" />
          </label>
          <label class="flex flex-col gap-1 text-sm">
            Income weight
            <input v-model.number="form.incomeWeight" type="number" step="0.1" min="0" max="1" class="rounded border border-gray-300 p-2" />
          </label>
        </CardContent>
      </Card>

      <Card class="bg-primary-foreground">
        <CardHeader><CardTitle>Output & database</CardTitle></CardHeader>
        <CardContent class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <label class="flex flex-col gap-1 text-sm">
            Output directory
            <input v-model="form.outputDir" class="rounded border border-gray-300 p-2" />
          </label>
          <label class="flex flex-col gap-1 text-sm">
            CSV filename
            <input v-model="form.csvFilename" class="rounded border border-gray-300 p-2" />
          </label>
          <label class="flex flex-col gap-1 text-sm">
            Markdown filename
            <input v-model="form.mdFilename" class="rounded border border-gray-300 p-2" />
          </label>
          <label class="flex flex-col gap-1 text-sm">
            Postgres URL (empty = DB disabled)
            <input v-model="form.databaseUrl" class="rounded border border-gray-300 p-2 font-mono text-xs" />
          </label>
        </CardContent>
      </Card>

      <div class="flex items-center gap-4">
        <Button type="submit" :disabled="saving">
          {{ saving ? "Saving…" : "Save settings" }}
        </Button>
        <span v-if="saveOk" class="text-green-600 text-sm">Saved.</span>
        <span v-if="saveError" class="text-red-600 text-sm">{{ saveError }}</span>
      </div>
    </form>
  </div>
</template>
