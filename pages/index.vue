<script setup lang="ts">
import type { Job } from "@/lib/types";

definePageMeta({
  layout: "simple",
});

const sampleData: Array<Job> = [
  {
    id: 1,
    company: "Photosnap",
    logo: "photosnap.svg",
    new: true,
    featured: true,
    position: "Senior Frontend Developer",
    role: "Frontend",
    level: "Senior",
    postedAt: "1d ago",
    contract: "Full Time",
    location: "USA Only",
    languages: ["HTML", "CSS", "JavaScript"],
    tools: [],
  },
  {
    id: 2,
    company: "Photosnap",
    logo: "photosnap.svg",
    new: true,
    featured: true,
    position: "Senior Frontend Developer",
    role: "Frontend",
    level: "Senior",
    postedAt: "1d ago",
    contract: "Full Time",
    location: "USA Only",
    languages: ["HTML", "CSS", "JavaScript"],
    tools: [],
  },
];
</script>

<template>
  <div>
    <div class="relative h-40 pt-32">
      <JobFilter />
      <JobList :job-data="sampleData" />
    </div>
  </div>
</template>
