<template>
  <aside class="w-64 min-h-screen flex flex-col bg-white text-gray-800 relative overflow-hidden border-r border-primary-light/50">
    <!-- 装饰光晕 -->
    <div class="absolute top-0 left-0 w-64 h-64 bg-primary/10 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>
    <div class="absolute bottom-0 right-0 w-64 h-64 bg-accent-blue/20 rounded-full blur-3xl translate-x-1/2 translate-y-1/2 pointer-events-none"></div>

    <div class="p-6 relative z-10">
      <div class="flex items-center space-x-2">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-accent-blue flex items-center justify-center shadow-lg shadow-primary/20">
          <SparklesIcon class="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 class="text-lg font-bold text-gray-800">商家后台</h1>
          <p class="text-xs text-primary">AI电商运营管理中心</p>
        </div>
      </div>
    </div>

    <nav class="flex-1 px-4 space-y-1.5 relative z-10">
      <router-link
        v-for="item in menu"
        :key="item.path"
        :to="item.path"
        :class="isActive(item.path) ? 'bg-primary-light text-primary shadow-sm shadow-primary/10 translate-x-1' : 'hover:bg-primary-light/50 hover:translate-x-1 text-gray-600 hover:text-primary'"
        class="flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 group"
      >
        <component :is="item.icon" class="w-5 h-5" :class="isActive(item.path) ? 'text-primary' : 'text-primary/70 group-hover:text-primary'" />
        <span class="text-sm font-medium">{{ item.name }}</span>
        <div v-if="isActive(item.path)" class="ml-auto w-1.5 h-1.5 rounded-full bg-primary"></div>
      </router-link>
    </nav>

    <div class="p-4 relative z-10">
      <div class="bg-page rounded-2xl p-4 border border-primary-light/50">
        <div class="flex items-center space-x-3 mb-3">
          <img
            v-if="auth.user?.avatar_url"
            :src="auth.user.avatar_url.startsWith('http') ? auth.user.avatar_url : baseUrl + auth.user.avatar_url"
            class="w-10 h-10 rounded-full object-cover"
          />
          <div
            v-else
            class="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-accent-blue flex items-center justify-center text-sm font-bold text-white"
          >
            {{ (auth.user?.nickname || auth.user?.username || 'M').charAt(0).toUpperCase() }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-medium truncate">{{ auth.user?.nickname || auth.user?.username }}</div>
            <div class="text-xs text-primary">商家管理员</div>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-2">
          <router-link to="/merchant/profile" class="flex items-center justify-center space-x-1 text-primary hover:text-white hover:bg-primary rounded-xl py-2 text-sm transition-all duration-200">
            <UserCircleIcon class="w-4 h-4" />
            <span>个人中心</span>
          </router-link>
          <button @click="logout" class="flex items-center justify-center space-x-1 text-red-500 hover:text-white hover:bg-red-500 rounded-xl py-2 text-sm transition-all duration-200">
            <ArrowLeftOnRectangleIcon class="w-4 h-4" />
            <span>退出登录</span>
          </button>
        </div>
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
  UserCircleIcon,
} from '@heroicons/vue/24/outline'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const baseUrl = 'http://127.0.0.1:8000'

const menu = [
  { name: '数据看板', path: '/merchant/dashboard', icon: ChartPieIcon },
  { name: '商品管理', path: '/merchant/products', icon: CubeIcon },
  { name: 'AI文案生成', path: '/merchant/ai-copy', icon: SparklesIcon },
  { name: '知识库管理', path: '/merchant/knowledge', icon: BookOpenIcon },
  { name: '商品评论', path: '/merchant/reviews', icon: ChatBubbleLeftRightIcon },
  { name: '直播/短视频脚本', path: '/merchant/live-script', icon: VideoCameraIcon },
  { name: '订单管理', path: '/merchant/orders', icon: ClipboardDocumentListIcon },
  { name: '客服管理', path: '/merchant/customer-service', icon: ChatBubbleLeftRightIcon },
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
