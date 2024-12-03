<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { Icon } from "@iconify/vue";

const props = defineProps({
  selectedTags: {
    type: [Array<string>],
    default: [],
  },
});
</script>

<template>
  <header
    class="p-4 mx-auto w-11/12 md:w-9/12 rounded shadow-lg bg-primary-foreground"
  >
    <div class="flex place-items-center justify-between px-1 md:px-6">
      <div class="overflow-x-hidden">
        <Button
          variant="outline"
          class="my-2 px-0 mr-4 rounded-r bg-secondary hover:text-primary"
          v-for="(item, index) in props.selectedTags"
          :key="index"
        >
          <span class="px-2 text-primary font-bold text-lg hover:text-primary">
            {{ item }}
          </span>
          <Button
            class="px-2 bg-primary hover:bg-foreground"
            @click="$emit('removeTag', item)"
          >
            <Icon
              class="text-primary-foreground text-lg font-black"
              icon="radix-icons:cross-1"
            />
          </Button>
        </Button>
      </div>

      <Button @click="$emit('clearTags')" class="font-black" variant="link">
        Clear
      </Button>
    </div>
  </header>
</template>
