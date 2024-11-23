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
    class="p-4 mx-auto mb-4 w-9/12 rounded shadow-lg bg-primary-foreground"
  >
    <div class="flex px-6">
      <div
        class="flex flex-wrap overflow-x-hidden"
        v-for="(item, index) in props.selectedTags"
        :key="index"
      >
        <Button
          class="px-2 rounded-l text-primary font-bold text-lg hover:text-primary"
          variant="outline"
        >
          {{ item }}
        </Button>
        <Button
          class="px-2 mr-4 rounded-r bg-primary hover:bg-foreground hover:text-primary"
          variant="outline"
          @click="$emit('removeTag', item)"
        >
          <Icon
            icon="radix-icons:cross-1"
            class="text-primary-foreground text-lg font-black"
          />
        </Button>
      </div>

      <Button
        @click="$emit('clearTags')"
        class="ml-auto font-black"
        variant="link"
      >
        Clear
      </Button>
    </div>
  </header>
</template>
