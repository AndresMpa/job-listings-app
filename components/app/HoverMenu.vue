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
      <div class="flex justify-end">
        <Button class="hover:bg-inherit" variant="ghost">
          <Icon
            icon="radix-icons:hamburger-menu"
            class="text-primary-foreground rotate-0 scale-100 transition-all"
          />
        </Button>
      </div>
    </SheetTrigger>
    <SheetContent :side="'right'">
      <SheetHeader>
        <SheetTitle>Edit profile</SheetTitle>
        <SheetDescription>
          Make changes to your profile here. Click save when you're done.
        </SheetDescription>
      </SheetHeader>
      <slot />
      <SheetFooter>
        <SheetClose as-child>
          <Button>Close</Button>
        </SheetClose>
      </SheetFooter>
    </SheetContent>
  </Sheet>
</template>
