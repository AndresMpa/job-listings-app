<script setup lang="ts">
import { Home, Inbox, Search, Settings } from '@lucide/vue'
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
const items = [
  {
    title: 'Home',
    url: '/',
    icon: Home,
  },
  {
    title: 'Jobs',
    url: '/jobs',
    icon: Inbox,
  },
  {
    title: 'Profiles',
    url: '/Profiles',
    icon: Search,
  },
  {
    title: 'Settings',
    url: '/settings',
    icon: Settings,
  },
]
</script>
<template>
  <Sidebar side="right" class="bg-primary-foreground text-foreground">
    <SidebarContent>
      <SidebarGroup>
        <SidebarGroupLabel>Application</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in items" :key="item.title">
              <SidebarMenuButton as-child>
                <NuxtLink :to="item.url" class="text-primary font-bold my-auto hover:underline">
                  <component :is="item.icon" />
                  <span>{{ item.title }}</span>
                </NuxtLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
      <SidebarGroup>
        <SidebarGroupLabel>Tools</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem class="flex justify-center">
              <UtilLanguageSwitcher />
            </SidebarMenuItem>
            <SidebarMenuItem class="flex justify-center">
              <UtilThemeSwitcher />
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>
    <SidebarFooter>
      <span v-show="profileName">{{profileName}}</span>
    </SidebarFooter>
  </Sidebar>
</template>
