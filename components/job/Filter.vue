<script setup lang="ts">
import { Button } from "@/components/ui/button";
</script>

<template>
  <header
    class="p-4 mx-auto mb-4 w-9/12 rounded shadow-lg bg-primary-foreground"
  >
    <div class="flex px-2">
      <UtilThemeSwitcher />

      <Button class="ml-auto font-bold" variant="link">Clear</Button>
    </div>
  </header>
</template>
