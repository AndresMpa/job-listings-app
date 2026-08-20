<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import type { ProfileSettings } from "@/lib/types";

definePageMeta({
  layout: "simple",
});

const { data: profiles } = await useFetch<ProfileSettings[]>("/api/profiles");

function initials(name: string) {
  return name
    .split(/[\s._-]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((s) => s[0]?.toUpperCase())
    .join("");
}
</script>

<template>
  <div class="relative pb-20 max-w-5xl mx-auto px-4">
    <h1 class="text-3xl font-bold text-primary-foreground mb-8">Profiles</h1>

    <div v-if="!profiles" class="text-primary-foreground">Loading profiles…</div>

    <p v-else-if="profiles.length === 0" class="text-primary-foreground">
      No profiles yet — add one via
      <code>PUT /profiles/&lt;name&gt;</code> or in Settings.
    </p>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
      <Card v-for="p in profiles" :key="p.name" class="bg-primary-foreground overflow-hidden">
        <CardContent class="flex flex-col items-center gap-3 pt-6">
          <div
            class="w-20 h-20 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xl font-bold"
          >
            {{ initials(p.name) }}
          </div>
          <div class="text-center">
            <p class="font-semibold text-lg">{{ p.name }}</p>
            <p class="text-sm text-muted-foreground line-clamp-1">{{ p.profile || "Candidate" }}</p>
          </div>
          <NuxtLink :to="`/jobs/${p.name}`">
            <Button>View jobs</Button>
          </NuxtLink>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
