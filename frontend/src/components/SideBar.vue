<template>
  <aside class="w-64 min-h-screen flex flex-col bg-gradient-to-b from-slate-900 via-indigo-950 to-slate-900 text-white relative overflow-hidden">
    <!-- 装饰光晕 -->
    <div class="absolute top-0 left-0 w-64 h-64 bg-indigo-600/20 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>
    <div class="absolute bottom-0 right-0 w-64 h-64 bg-pink-600/10 rounded-full blur-3xl translate-x-1/2 translate-y-1/2 pointer-events-none"></div>

    <div class="p-6 relative z-10">
      <div class="flex items-center space-x-2">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-pink-500 flex items-center justify-center shadow-lg">
          <SparklesIcon class="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 class="text-lg font-bold">商家后台</h1>
          <p class="text-xs text-indigo-200">AI电商运营管理中心</p>
        </div>
      </div>
    </div>

    <nav class="flex-1 px-4 space-y-1.5 relative z-10">
      <router-link
        v-for="item in menu"
        :key="item.path"
        :to="item.path"
        :class="isActive(item.path) ? 'bg-gradient-to-r from-indigo-600 to-violet-600 shadow-lg shadow-indigo-900/30 translate-x-1' : 'hover:bg-white/5 hover:translate-x-1 text-gray-300 hover:text-white'"
        class="flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 group"
      >
        <component :is="item.icon" class="w-5 h-5" :class="isActive(item.path) ? 'text-white' : 'text-indigo-300 group-hover:text-white'" />
        <span class="text-sm font-medium">{{ item.name }}</span>
        <div v-if="isActive(item.path)" class="ml-auto w-1.5 h-1.5 rounded-full bg-white"></div>
      </router-link>
    </nav>

    <div class="p-4 relative z-10">
      <div class="bg-white/5 rounded-2xl p-4 border border-white/10">
        <div class="flex items-center space-x-3 mb-3">
          <div class="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-pink-500 flex items-center justify-center text-sm font-bold">
            {{ (auth.user?.nickname || auth.user?.username || 'M').charAt(0).toUpperCase() }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-medium truncate">{{ auth.user?.nickname || auth.user?.username }}</div>
            <div class="text-xs text-indigo-200">商家管理员</div>
          </div>
        </div>
        <button @click="logout" class="w-full flex items-center justify-center space-x-2 text-red-300 hover:text-white hover:bg-red-500/20 rounded-xl py-2 text-sm transition-all duration-200">
          <ArrowLeftOnRectangleIcon class="w-4 h-4" />
          <span>退出登录</span>
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import {
  ChartPieIcon,
  CubeIcon,
  SparklesIcon,
  BookOpenIcon,
  ChatBubbleLeftRightIcon,
  VideoCameraIcon,
  ClipboardDocumentListIcon,
  UsersIcon,
  ArrowLeftOnRectangleIcon,
} from '@heroicons/vue/24/outline'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const menu = [
  { name: '数据看板', path: '/merchant/dashboard', icon: ChartPieIcon },
  { name: '商品管理', path: '/merchant/products', icon: CubeIcon },
  { name: 'AI文案生成', path: '/merchant/ai-copy', icon: SparklesIcon },
  { name: '知识库管理', path: '/merchant/knowledge', icon: BookOpenIcon },
  { name: '商品评论', path: '/merchant/reviews', icon: ChatBubbleLeftRightIcon },
  { name: '直播/短视频脚本', path: '/merchant/live-script', icon: VideoCameraIcon },
  { name: '订单管理', path: '/merchant/orders', icon: ClipboardDocumentListIcon },
  { name: '管理员管理', path: '/merchant/admin-management', icon: UsersIcon },
]

function isActive(path) {
  return route.path === path
}

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
