<script setup lang="ts">
import { Button } from "@/components/ui/button";

definePageMeta({
  layout: "simple",
});
</script>

<template>
  <div class="relative pt-40 pb-20 max-w-2xl mx-auto px-4 text-center">
    <h1 class="text-4xl font-bold text-primary-foreground mb-4">Job Search Automation</h1>
    <p class="text-primary-foreground/80 mb-10">
      Fetches, scores, and reports job listings across multiple sources — one search per candidate profile.
    </p>
    <div class="flex flex-wrap justify-center gap-4">
      <NuxtLink to="/profiles"><Button size="lg">Profiles</Button></NuxtLink>
      <NuxtLink to="/jobs"><Button size="lg" variant="secondary">All jobs</Button></NuxtLink>
      <NuxtLink to="/settings"><Button size="lg" variant="secondary">Settings</Button></NuxtLink>
    </div>
  </div>
</template>
