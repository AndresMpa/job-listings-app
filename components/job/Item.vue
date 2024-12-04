<script setup lang="ts">
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

import { getImagePath } from "~/lib/images";

const props = defineProps({
  job: {
    type: [Object],
    required: true,
  },
  tags: {
    type: [Array<string>],
    default: [],
  },
});
</script>

<template>
  <ul
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
            <img
              class="mx-8 md:mx-5"
              :src="getImagePath(props.job.logo)"
              :alt="props.job.company"
            />
          </figure>
        </div>

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

          <h2 class="mb-2 mt-2 text-2xl font-bold hover:text-primary">
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

        <div
          class="block md:hidden w-full my-5 border-t-2 border-gray-200"
        ></div>

        <div class="block md:flex md:ml-auto">
          <Button
            v-for="(langOrTool, index) in [].concat(
              props.job.role,
              props.job.level,
              props.job.languages,
              props.job.tools
            )"
            :key="langOrTool + index"
            :index="index"
            @click="$emit('addTag', langOrTool)"
            :class="[
              tags.includes(langOrTool)
                ? 'bg-primary text-primary-foreground'
                : 'text-primary',
              'my-2 mx-2 font-bold text-lg rounded hover:bg-primary hover:text-primary-foreground',
            ]"
            variant="outline"
          >
            {{ langOrTool }}
          </Button>
        </div>
      </CardContent>
    </Card>
  </ul>
</template>
