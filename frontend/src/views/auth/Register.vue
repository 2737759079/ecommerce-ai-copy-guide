<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-700 via-violet-700 to-pink-600 p-6 relative overflow-hidden">
    <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-400/30 rounded-full blur-3xl float pointer-events-none"></div>
    <div class="absolute bottom-1/4 right-1/4 w-80 h-80 bg-pink-400/30 rounded-full blur-3xl float pointer-events-none" style="animation-delay: 2s"></div>
    <div class="absolute inset-0 opacity-20 pointer-events-none" style="background-image: radial-gradient(circle at 2px 2px, rgba(255,255,255,0.15) 1px, transparent 0); background-size: 32px 32px;"></div>

    <div class="glass rounded-3xl shadow-2xl w-full max-w-md p-8 border border-white/30 relative z-10">
      <div class="text-center mb-8">
        <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-600 to-pink-500 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-indigo-500/30">
          <UserPlusIcon class="w-7 h-7 text-white" />
        </div>
        <h2 class="text-2xl font-bold text-gray-800">用户注册</h2>
        <p class="text-sm text-gray-500 mt-2">创建您的专属账号，开启智能电商体验</p>
      </div>

      <div class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">昵称（用于登录，不可重复）</label>
          <div class="relative">
            <UserIcon class="w-5 h-5 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input v-model="form.nickname" type="text" class="input-modern pl-11" placeholder="请输入昵称" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">密码</label>
          <div class="relative">
            <LockClosedIcon class="w-5 h-5 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input v-model="form.password" type="password" class="input-modern pl-11" placeholder="至少6位" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">确认密码</label>
          <div class="relative">
            <LockClosedIcon class="w-5 h-5 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input v-model="form.confirmPassword" type="password" class="input-modern pl-11" placeholder="再次输入密码" @keydown.enter="handleRegister" />
          </div>
        </div>
        <button @click="handleRegister" :disabled="loading" class="w-full btn-primary py-3 text-base flex items-center justify-center space-x-2">
          <svg v-if="loading" class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span>{{ loading ? '注册中...' : '注册' }}</span>
        </button>
        <p v-if="error" class="text-red-500 text-sm text-center shake">{{ error }}</p>
        <p v-if="success" class="text-green-600 text-sm text-center fade-in-up">注册成功，请登录</p>
      </div>

      <div class="mt-8 text-center text-sm text-gray-500">
        <router-link to="/login" class="text-indigo-600 hover:text-indigo-700 font-medium hover:underline">已有账号？去登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { UserIcon, UserPlusIcon, LockClosedIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const error = ref('')
const success = ref(false)
const form = reactive({ nickname: '', password: '', confirmPassword: '' })

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
