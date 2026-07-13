<template>
  <nav class="sticky top-0 z-50 glass border-b border-white/20 shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16 items-center">
        <div class="flex items-center space-x-8">
          <router-link to="/home" class="flex items-center space-x-2 text-xl font-bold text-gradient">
            <SparklesIcon class="w-6 h-6 text-indigo-600" />
            <span>AI电商助手</span>
          </router-link>
          <div class="hidden md:flex space-x-1">
            <router-link
              v-for="item in menu"
              :key="item.path"
              :to="item.path"
              :class="route.path === item.path ? 'text-indigo-600 bg-indigo-50' : 'text-gray-600 hover:text-indigo-600 hover:bg-gray-50'"
              class="flex items-center space-x-1.5 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200"
            >
              <component :is="item.icon" class="w-4 h-4" />
              <span>{{ item.name }}</span>
            </router-link>
          </div>
        </div>
        <div class="flex items-center space-x-4">
          <div class="flex items-center space-x-2 bg-gray-50 rounded-full pl-3 pr-1 py-1">
            <div class="w-7 h-7 rounded-full bg-gradient-to-br from-indigo-500 to-pink-500 flex items-center justify-center text-white text-xs font-bold">
              {{ (auth.user?.nickname || auth.user?.username || 'U').charAt(0).toUpperCase() }}
            </div>
            <span class="text-sm text-gray-700 font-medium hidden sm:block">{{ auth.user?.nickname || auth.user?.username }}</span>
          </div>
          <button @click="logout" class="flex items-center space-x-1 text-sm text-red-500 hover:text-white hover:bg-red-500 px-3 py-1.5 rounded-full transition-all duration-200">
            <ArrowRightOnRectangleIcon class="w-4 h-4" />
            <span class="hidden sm:inline">退出</span>
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import {
  HomeIcon,
  ShoppingBagIcon,
  ShoppingCartIcon,
  UserIcon,
  SparklesIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/vue/24/outline'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const menu = [
  { name: '首页', path: '/home', icon: HomeIcon },
  { name: '我的订单', path: '/orders', icon: ShoppingBagIcon },
  { name: '购物车', path: '/cart', icon: ShoppingCartIcon },
  { name: '个人中心', path: '/profile', icon: UserIcon },
]

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
