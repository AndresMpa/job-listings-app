<script setup lang="ts">
import { computed } from "vue";

import type { Job } from "@/lib/types";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const props = defineProps<{ job: Job }>();

const images = import.meta.glob("assets/logos/*", { eager: true });

const logoSrc = computed(() => {
  const path = `/assets/logos/${props.job.logo}`;
  return (images[path] as any)?.default || "";
});
</script>

<template>
  <ul
    class="mb-1 mx-auto w-9/12 rounded shadow-xl bg-primary-foreground border-l-4 border-transparent hover:border-primary transition-colors duration-300"
  >
    <Card class="bg-primary-foreground py-3">
      <CardContent class="flex my-auto items-center">
        <img class="mx-5" :src="logoSrc" :alt="props.job.company" />

        <div class="flex flex-col">
          <div class="flex flex-row">
            <h3 class="text-lg text-primary font-bold">
              {{ props.job.company }}
            </h3>

            <div class="flex items-center justify-center mx-5">
              <Badge v-if="props.job.new" class="uppercase bg-primary mx-2">
                New!
              </Badge>
              <Badge v-if="props.job.featured" class="uppercase bg-foreground">
                Featured
              </Badge>
            </div>
          </div>

          <h2 class="mt-2 mb-0 text-2xl font-bold hover:text-primary">
            {{ props.job.position }}
          </h2>

          <p class="text-gray-500 text-lg font-extralight">
            <span> {{ props.job.postedAt }} </span>
            <span class="mx-2"> - </span>
            <span> {{ props.job.contract }} </span>
            <span class="mx-2"> - </span>
            <span> {{ props.job.location }} </span>
          </p>
        </div>

        <div class="flex ml-auto">
          <div
            v-for="(langOrTool, index) in props.job.languages.concat(
              props.job.tools
            )"
            :key="langOrTool + index"
            :index="index"
          >
            <Button
              class="mx-2 text-primary font-bold text-lg rounded hover:bg-primary hover:text-primary-foreground"
              variant="outline"
            >
              {{ langOrTool }}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  </ul>
</template>
