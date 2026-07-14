<template>
  <div class="min-h-screen flex bg-gradient-to-br from-page via-white to-accent-blue/30 relative overflow-hidden">
    <!-- 装饰背景 -->
    <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl float pointer-events-none"></div>
    <div class="absolute bottom-1/4 right-1/4 w-80 h-80 bg-accent-blue/30 rounded-full blur-3xl float pointer-events-none" style="animation-delay: 2s"></div>
    <div class="absolute inset-0 opacity-20 pointer-events-none" style="background-image: radial-gradient(circle at 2px 2px, rgba(155,135,245,0.08) 1px, transparent 0); background-size: 32px 32px;"></div>

    <!-- 左侧宣传 -->
    <div class="hidden lg:flex w-1/2 flex-col justify-center px-20 text-primary-dark relative z-10">
      <div class="inline-flex items-center space-x-2 bg-white/70 backdrop-blur-sm rounded-full px-4 py-2 w-fit mb-8 border border-primary-light/50 shadow-sm">
        <SparklesIcon class="w-5 h-5 text-primary" />
        <span class="text-sm font-medium">AI 驱动的电商运营助手</span>
      </div>
      <h1 class="text-5xl font-bold mb-6 leading-tight">电商AI商品文案<br/>生成与智能导购助手</h1>
      <p class="text-lg opacity-80 mb-10 max-w-md">为商家提供AI文案、RAG导购、评论分析；为用户提供智能购物、AI咨询、模拟下单。</p>
      <div class="grid grid-cols-2 gap-4 max-w-md">
        <div v-for="(feat, idx) in features" :key="idx" class="bg-white/70 backdrop-blur-sm rounded-2xl p-4 border border-primary-light/50 shadow-sm hover:bg-white/80 transition-colors">
          <component :is="feat.icon" class="w-6 h-6 mb-2 text-primary" />
          <p class="text-sm text-gray-700">{{ feat.text }}</p>
        </div>
      </div>
    </div>

    <!-- 右侧登录卡片 -->
    <div class="w-full lg:w-1/2 flex items-center justify-center p-6 relative z-10">
      <div class="glass rounded-3xl shadow-2xl w-full max-w-md p-8 border border-primary-light/50">
        <div class="text-center mb-8">
          <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary to-accent-blue flex items-center justify-center mx-auto mb-4 shadow-lg shadow-primary/30">
            <SparklesIcon class="w-7 h-7 text-white" />
          </div>
          <h2 class="text-2xl font-bold text-gray-800">欢迎登录</h2>
          <p class="text-sm text-gray-500 mt-2">请选择身份并登录您的账号</p>
        </div>

        <div class="flex justify-center mb-6 p-1 bg-gray-100/80 rounded-xl">
          <button
            v-for="r in roles"
            :key="r.value"
            @click="form.role = r.value"
            :class="form.role === r.value ? 'bg-white shadow-md text-primary' : 'text-gray-500 hover:text-gray-700'"
            class="flex-1 flex items-center justify-center space-x-1.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200"
          >
            <component :is="r.icon" class="w-4 h-4" />
            <span>{{ r.label }}</span>
          </button>
        </div>

        <div class="space-y-5">
          <FormInput v-model="form.username" type="text" :icon="UserIcon" :label="form.role === 'user' ? '昵称' : '账号'" :placeholder="form.role === 'user' ? '请输入昵称' : '请输入账号'" @keydown.enter="handleLogin" />
          <FormInput v-model="form.password" type="password" :icon="LockClosedIcon" label="密码" placeholder="请输入密码" @keydown.enter="handleLogin" />
          <button @click="handleLogin" :disabled="loading" class="w-full btn-primary py-3 text-base flex items-center justify-center space-x-2">
            <ArrowRightIcon v-if="!loading" class="w-5 h-5" />
            <svg v-else class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            <span>{{ loading ? '登录中...' : '登录' }}</span>
          </button>
          <p v-if="error" class="text-red-500 text-sm text-center shake">{{ error }}</p>
        </div>

        <div class="mt-8 text-center text-sm text-gray-500 space-x-6">
          <router-link to="/register" class="text-primary hover:text-primary-dark font-medium hover:underline">用户注册</router-link>
          <router-link to="/forgot-password" class="text-primary hover:text-primary-dark font-medium hover:underline">找回密码</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import FormInput from '../../components/ui/FormInput.vue'
import {
  SparklesIcon,
  UserIcon,
  UsersIcon,
  ShieldCheckIcon,
  LockClosedIcon,
  ArrowRightIcon,
  DocumentTextIcon,
  ChatBubbleLeftRightIcon,
  ShoppingBagIcon,
} from '@heroicons/vue/24/outline'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const error = ref('')
const form = reactive({ username: '', password: '', role: 'user' })

const roles = [
  { value: 'user', label: '普通用户', icon: UserIcon },
  { value: 'merchant', label: '商家管理员', icon: ShieldCheckIcon },
]

const features = [
  { icon: DocumentTextIcon, text: 'AI自动生成商品文案与直播脚本' },
  { icon: ChatBubbleLeftRightIcon, text: '基于私有知识库的智能导购问答' },
  { icon: ShoppingBagIcon, text: '评论情感分析与商品优化建议' },
  { icon: UsersIcon, text: '统一登录，商家/用户双端闭环' },
]

async function handleLogin() {
  if (!form.username || !form.password) {
    error.value = '请输入账号和密码'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await auth.login(form)
    router.push(form.role === 'merchant' ? '/merchant' : '/home')
  } catch (e) {
    error.value = e.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>
