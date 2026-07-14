<template>
  <div class="min-h-screen flex bg-gradient-to-br from-page via-white to-accent-blue/30 relative overflow-hidden">
    <!-- 装饰背景 -->
    <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl float pointer-events-none"></div>
    <div class="absolute bottom-1/4 right-1/4 w-80 h-80 bg-accent-blue/30 rounded-full blur-3xl float pointer-events-none" style="animation-delay: 2s"></div>
    <div class="absolute inset-0 opacity-20 pointer-events-none" style="background-image: radial-gradient(circle at 2px 2px, rgba(155,135,245,0.08) 1px, transparent 0); background-size: 32px 32px;"></div>

    <!-- 左侧宣传 -->
    <div class="hidden lg:flex w-1/2 flex-col justify-center px-20 text-primary-dark relative z-10">
      <div class="inline-flex items-center space-x-2 bg-white/70 backdrop-blur-sm rounded-full px-4 py-2 w-fit mb-8 border border-primary-light/50 shadow-sm">
        <KeyIcon class="w-5 h-5 text-primary" />
        <span class="text-sm font-medium">账号安全中心</span>
      </div>
      <h1 class="text-5xl font-bold mb-6 leading-tight">忘记密码？<br/>轻松找回</h1>
      <p class="text-lg opacity-80 mb-10 max-w-md">验证账号后即可重置密码，保障您的账号安全，购物无忧。</p>
      <div class="grid grid-cols-2 gap-4 max-w-md">
        <div v-for="(feat, idx) in features" :key="idx" class="bg-white/70 backdrop-blur-sm rounded-2xl p-4 border border-primary-light/50 shadow-sm hover:bg-white/80 transition-colors">
          <component :is="feat.icon" class="w-6 h-6 mb-2 text-primary" />
          <p class="text-sm text-gray-700">{{ feat.text }}</p>
        </div>
      </div>
    </div>

    <!-- 右侧找回密码卡片 -->
    <div class="w-full lg:w-1/2 flex items-start justify-center pt-12 lg:pt-16 p-6 relative z-10">
      <div class="glass rounded-3xl shadow-2xl w-full max-w-md p-8 border border-primary-light/50">
        <div class="text-center mb-8">
          <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary to-accent-blue flex items-center justify-center mx-auto mb-4 shadow-lg shadow-primary/30">
            <KeyIcon class="w-7 h-7 text-white" />
          </div>
          <h2 class="text-2xl font-bold text-gray-800">找回密码</h2>
          <p class="text-sm text-gray-500 mt-2">验证账号后即可重置密码</p>
        </div>

        <div v-if="step === 1" class="space-y-5 fade-in-up">
          <FormInput v-model="username" type="text" :icon="UserIcon" label="账号" placeholder="请输入账号" @keydown.enter="verifyAccount" />
          <button @click="verifyAccount" :disabled="loading" class="w-full btn-primary py-3 text-base flex items-center justify-center space-x-2">
            <span>{{ loading ? '校验中...' : '下一步' }}</span>
            <ArrowRightIcon v-if="!loading" class="w-5 h-5" />
          </button>
        </div>

        <div v-else class="space-y-5 fade-in-up">
          <div class="bg-primary-light rounded-xl p-4 flex items-center space-x-3">
            <UserCircleIcon class="w-8 h-8 text-primary" />
            <div>
              <p class="text-xs text-gray-500">当前账号</p>
              <p class="text-sm font-medium text-gray-800">{{ username }}</p>
            </div>
          </div>
          <FormInput v-model="newPassword" type="password" :icon="LockClosedIcon" label="新密码" placeholder="请输入新密码" @keydown.enter="resetPassword" />
          <FormInput v-model="confirmPassword" type="password" :icon="LockClosedIcon" label="确认新密码" placeholder="请再次输入新密码" @keydown.enter="resetPassword" />
          <button @click="resetPassword" :disabled="loading" class="w-full btn-primary py-3 text-base flex items-center justify-center space-x-2">
            <KeyIcon v-if="!loading" class="w-5 h-5" />
            <svg v-else class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            <span>{{ loading ? '重置中...' : '重置密码' }}</span>
          </button>
        </div>

        <p v-if="error" class="text-red-500 text-sm text-center mt-4 shake">{{ error }}</p>
        <p v-if="success" class="text-green-600 text-sm text-center mt-4 fade-in-up">密码重置成功，请登录</p>

        <div class="mt-8 text-center text-sm text-gray-500">
          <router-link to="/login" class="text-primary hover:text-primary-dark font-medium hover:underline flex items-center justify-center space-x-1">
            <ArrowLeftIcon class="w-4 h-4" />
            <span>返回登录</span>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api/axios'
import FormInput from '../../components/ui/FormInput.vue'
import {
  UserIcon,
  KeyIcon,
  LockClosedIcon,
  ArrowRightIcon,
  ArrowLeftIcon,
  UserCircleIcon,
  ShieldCheckIcon,
  FingerPrintIcon,
  LockClosedIcon as SecurityIcon,
  ClipboardDocumentCheckIcon,
} from '@heroicons/vue/24/outline'

const router = useRouter()
const step = ref(1)
const username = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(false)

const features = [
  { icon: ShieldCheckIcon, text: '账号安全保护' },
  { icon: SecurityIcon, text: '密码加密存储' },
  { icon: FingerPrintIcon, text: '身份快速核验' },
  { icon: ClipboardDocumentCheckIcon, text: '重置即时生效' },
]

async function verifyAccount() {
  if (!username.value) {
    error.value = '请输入账号'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await api.post('/auth/forgot-password', { username: username.value, new_password: '' })
    step.value = 2
  } catch (e) {
    error.value = e.response?.data?.detail || '账号不存在'
  } finally {
    loading.value = false
  }
}

async function resetPassword() {
  if (newPassword.value.length < 6) {
    error.value = '密码至少6位'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    error.value = '两次密码不一致'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await api.post('/auth/reset-password', { username: username.value, new_password: newPassword.value })
    success.value = true
    setTimeout(() => router.push('/login'), 1000)
  } catch (e) {
    error.value = e.response?.data?.detail || '重置失败'
  } finally {
    loading.value = false
  }
}
</script>
