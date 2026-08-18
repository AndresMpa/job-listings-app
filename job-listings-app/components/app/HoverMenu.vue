<script setup lang="ts">
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Icon } from "@iconify/vue";
</script>

<template>
  <Sheet>
    <SheetTrigger as-child>
      <div class="flex justify-end" aria-labelledby="menuButton" role="button">
        <Button id="menuButton" aria-label="Menu" class="hover:bg-inherit" variant="ghost">
          <Icon
            icon="radix-icons:hamburger-menu"
            class="text-primary-foreground rotate-0 scale-100 transition-all"
          />
        </Button>
      </div>
    </SheetTrigger>
    <SheetContent :side="'right'" class="flex flex-col h-full">
      <SheetHeader>
        <SheetTitle>Job Listing App</SheetTitle>
        <div class="flex flex-row mr-5 justify-between">
          <SheetDescription>
            Helping you tracking jobs.
          </SheetDescription>
          <div class="flex flex-row justify-end">
            <UtilLanguageSwitcher />
            <UtilThemeSwitcher />
          </div>
        </div>
      </SheetHeader>
      <slot />
      <SheetFooter class="mt-auto">
        <SheetClose as-child>
          <Button>Close</Button>
        </SheetClose>
      </SheetFooter>
    </SheetContent>
  </Sheet>
</template>
