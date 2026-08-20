<script setup lang="ts">
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

const route = useRoute();
const profileName = computed(() => route.params.name as string);
</script>

<template>
  <Sidebar>
    <SidebarHeader>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton size="lg" as-child>


          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarHeader>

    <SidebarContent>
      <SidebarGroup>
        <SidebarGroupContent>
        <UtilLanguageSwitcher />
        <UtilThemeSwitcher />
        </SidebarGroupContent>
      </SidebarGroup>
      <SidebarGroup>
        <SidebarGroupContent>
        
          <slot />
        <div class="flex flex-col justify-start gap-y-2">
        <NuxtLink to="/" class="text-primary font-bold my-auto hover:underline">Home</NuxtLink>
        <NuxtLink to="/jobs" class="text-primary font-bold my-auto hover:underline">Jobs</NuxtLink>
        <NuxtLink to="/profiles" class="text-primary font-bold my-auto hover:underline">Profiles</NuxtLink>
        <NuxtLink to="/settings" class="text-primary font-bold my-auto hover:underline">Settings</NuxtLink>
      </div>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>

    <SidebarFooter>

            <NuxtLink to="/profiles">
              <span class="font-semibold">{{ profileName }}</span>
            </NuxtLink>
    </SidebarFooter>
  </Sidebar>
</template>
