<template>
  <div class="min-h-screen flex bg-gradient-to-br from-page via-white to-accent-blue/30 relative overflow-hidden">
    <!-- 装饰背景 -->
    <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl float pointer-events-none"></div>
    <div class="absolute bottom-1/4 right-1/4 w-80 h-80 bg-accent-blue/30 rounded-full blur-3xl float pointer-events-none" style="animation-delay: 2s"></div>
    <div class="absolute inset-0 opacity-20 pointer-events-none" style="background-image: radial-gradient(circle at 2px 2px, rgba(155,135,245,0.08) 1px, transparent 0); background-size: 32px 32px;"></div>

    <!-- 左侧宣传 -->
    <div class="hidden lg:flex w-1/2 flex-col justify-center px-20 text-primary-dark relative z-10">
      <div class="inline-flex items-center space-x-2 bg-white/70 backdrop-blur-sm rounded-full px-4 py-2 w-fit mb-8 border border-primary-light/50 shadow-sm">
        <UserPlusIcon class="w-5 h-5 text-primary" />
        <span class="text-sm font-medium">新用户注册通道</span>
      </div>
      <h1 class="text-5xl font-bold mb-6 leading-tight">开启智能电商<br/>购物新体验</h1>
      <p class="text-lg opacity-80 mb-10 max-w-md">注册即享 AI 导购、智能推荐、订单追踪等专属服务，让购物更简单。</p>
      <div class="grid grid-cols-2 gap-4 max-w-md">
        <div v-for="(feat, idx) in features" :key="idx" class="bg-white/70 backdrop-blur-sm rounded-2xl p-4 border border-primary-light/50 shadow-sm hover:bg-white/80 transition-colors">
          <component :is="feat.icon" class="w-6 h-6 mb-2 text-primary" />
          <p class="text-sm text-gray-700">{{ feat.text }}</p>
        </div>
      </div>
    </div>

    <!-- 右侧注册卡片 -->
    <div class="w-full lg:w-1/2 flex items-start justify-center pt-12 lg:pt-16 p-6 relative z-10">
      <div class="glass rounded-3xl shadow-2xl w-full max-w-md p-8 border border-primary-light/50">
        <div class="text-center mb-8">
          <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary to-accent-blue flex items-center justify-center mx-auto mb-4 shadow-lg shadow-primary/30">
            <UserPlusIcon class="w-7 h-7 text-white" />
          </div>
          <h2 class="text-2xl font-bold text-gray-800">用户注册</h2>
          <p class="text-sm text-gray-500 mt-2">创建您的专属账号，开启智能电商体验</p>
        </div>

        <div class="space-y-5">
          <FormInput v-model="form.nickname" type="text" :icon="UserIcon" label="昵称（用于登录，不可重复）" placeholder="请输入昵称" @keydown.enter="handleRegister" />
          <FormInput v-model="form.password" type="password" :icon="LockClosedIcon" label="密码" placeholder="请输入密码" @keydown.enter="handleRegister" />
          <FormInput v-model="form.confirmPassword" type="password" :icon="LockClosedIcon" label="确认密码" placeholder="请再次输入密码" @keydown.enter="handleRegister" />
          <button @click="handleRegister" :disabled="loading" class="w-full btn-primary py-3 text-base flex items-center justify-center space-x-2">
            <ArrowRightIcon v-if="!loading" class="w-5 h-5" />
            <svg v-else class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            <span>{{ loading ? '注册中...' : '注册' }}</span>
          </button>
          <p v-if="error" class="text-red-500 text-sm text-center shake">{{ error }}</p>
          <p v-if="success" class="text-green-600 text-sm text-center fade-in-up">注册成功，请登录</p>
        </div>

        <div class="mt-8 text-center text-sm text-gray-500">
          <router-link to="/login" class="text-primary hover:text-primary-dark font-medium hover:underline">已有账号？去登录</router-link>
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
  UserIcon,
  UserPlusIcon,
  LockClosedIcon,
  ArrowRightIcon,
  ShoppingBagIcon,
  HeartIcon,
  BellIcon,
  ChartBarIcon,
} from '@heroicons/vue/24/outline'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const error = ref('')
const success = ref(false)
const form = reactive({ nickname: '', password: '', confirmPassword: '' })

const features = [
  { icon: ShoppingBagIcon, text: '海量商品智能推荐' },
  { icon: HeartIcon, text: '收藏心仪好物' },
  { icon: BellIcon, text: '订单物流实时提醒' },
  { icon: ChartBarIcon, text: 'AI 购物决策辅助' },
]

async function handleRegister() {
  if (!form.nickname || !form.password) {
    error.value = '请填写完整信息'
    return
  }
  if (form.password.length < 6) {
    error.value = '密码至少6位'
    return
  }
  if (form.password !== form.confirmPassword) {
    error.value = '两次密码不一致'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await auth.register({ password: form.password, nickname: form.nickname })
    success.value = true
    setTimeout(() => router.push('/login'), 1000)
  } catch (e) {
    error.value = e.response?.data?.detail || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>
