<script setup lang="ts">
import { computed, ref } from "vue";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import type { Job } from "@/lib/types";

const props = defineProps<{
  job: Job;
  tags?: string[];
}>();

defineEmits<{ addTag: [tag: string] }>();

const initials = computed(
  () =>
    props.job.company
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((w) => w[0]?.toUpperCase())
      .join("") || "?",
);

const scoreTier = computed(() => {
  const income = props.job.incomeScore ?? 0;
  if (income >= 8) return "🟢🟢🟢";
  if (income >= 6) return "🟢🟢";
  return "🟢";
});

const chips = computed(() => [props.job.source, ...props.job.tags]);

const showOutreach = ref(false);
</script>

<template>
  <li
    class="mx-auto my-12 md:my-0 w-11/12 md:w-9/12 rounded shadow-xl bg-primary-foreground"
  >
    <Card
      class="bg-primary-foreground py-3 border-l-[5px] border-transparent hover:border-primary transition-colors duration-300"
    >
      <CardContent
        class="flex flex-col md:flex-row my-auto items-start md:items-center"
      >
        <div class="relative">
          <figure class="bottom-0 -right-7 absolute md:static">
            <div
              class="mx-8 md:mx-5 flex h-12 w-12 items-center justify-center rounded-full bg-primary text-primary-foreground font-bold"
            >
              {{ initials }}
            </div>
          </figure>
        </div>

        <div class="flex flex-col">
          <div class="flex flex-row items-center flex-wrap">
            <h3 class="text-lg text-primary font-bold">
              {{ job.company || "Unknown company" }}
            </h3>

            <div class="flex items-center justify-center mx-5">
              <Badge v-if="job.score !== null" class="uppercase bg-primary mx-2">
                {{ scoreTier }} {{ job.score }}/10
              </Badge>
            </div>
          </div>

          <a :href="job.url" target="_blank" rel="noopener noreferrer">
            <h2 class="mb-2 mt-2 text-2xl font-bold hover:text-primary">
              {{ job.title }}
            </h2>
          </a>

          <p class="text-lg font-extralight">
            <span v-if="job.salary">{{ job.salary }}</span>
            <span v-if="job.salary" class="mx-2">-</span>
            <span>{{ job.location || "Remote" }}</span>
          </p>

          <p v-if="job.reasoning" class="text-sm mt-2 max-w-2xl">
            {{ job.reasoning }}
          </p>

          <button
            v-if="job.outreachDraft"
            type="button"
            class="text-primary text-sm mt-2 text-left underline w-fit"
            @click="showOutreach = !showOutreach"
          >
            {{ showOutreach ? "Hide" : "Show" }} outreach draft
          </button>
          <p
            v-if="showOutreach && job.outreachDraft"
            class="text-sm mt-2 max-w-2xl whitespace-pre-line border-l-2 border-primary pl-3"
          >
            {{ job.outreachDraft }}
          </p>
        </div>

        <div
          class="block md:hidden w-full my-5 border-t-2 border-gray-200"
        ></div>

        <div class="block md:flex md:ml-auto md:flex-wrap md:max-w-xs">
          <Button
            v-for="(chip, index) in chips"
            :key="chip + index"
            @click="$emit('addTag', chip)"
            :class="[
              (tags ?? []).includes(chip)
                ? 'bg-primary text-primary-foreground'
                : 'text-primary',
              'my-2 mx-2 font-bold text-lg rounded hover:bg-primary hover:text-primary-foreground',
            ]"
            variant="outline"
          >
            {{ chip }}
          </Button>
        </div>
      </CardContent>
    </Card>
  </li>
</template>
