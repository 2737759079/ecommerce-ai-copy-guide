<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-700 via-violet-700 to-pink-600 p-6 relative overflow-hidden">
    <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-400/30 rounded-full blur-3xl float pointer-events-none"></div>
    <div class="absolute bottom-1/4 right-1/4 w-80 h-80 bg-pink-400/30 rounded-full blur-3xl float pointer-events-none" style="animation-delay: 2s"></div>
    <div class="absolute inset-0 opacity-20 pointer-events-none" style="background-image: radial-gradient(circle at 2px 2px, rgba(255,255,255,0.15) 1px, transparent 0); background-size: 32px 32px;"></div>

    <div class="glass rounded-3xl shadow-2xl w-full max-w-md p-8 border border-white/30 relative z-10">
      <div class="text-center mb-8">
        <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-600 to-pink-500 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-indigo-500/30">
          <KeyIcon class="w-7 h-7 text-white" />
        </div>
        <h2 class="text-2xl font-bold text-gray-800">找回密码</h2>
        <p class="text-sm text-gray-500 mt-2">验证账号后即可重置密码</p>
      </div>

      <div v-if="step === 1" class="space-y-5 fade-in-up">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">账号</label>
          <div class="relative">
            <UserIcon class="w-5 h-5 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input v-model="username" type="text" class="input-modern pl-11" placeholder="请输入账号" />
          </div>
        </div>
        <button @click="verifyAccount" :disabled="loading" class="w-full btn-primary py-3 text-base flex items-center justify-center space-x-2">
          <span>{{ loading ? '校验中...' : '下一步' }}</span>
          <ArrowRightIcon v-if="!loading" class="w-5 h-5" />
        </button>
      </div>

      <div v-else class="space-y-5 fade-in-up">
        <div class="bg-indigo-50 rounded-xl p-4 flex items-center space-x-3">
          <UserCircleIcon class="w-8 h-8 text-indigo-600" />
          <div>
            <p class="text-xs text-gray-500">当前账号</p>
            <p class="text-sm font-medium text-gray-800">{{ username }}</p>
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">新密码</label>
          <div class="relative">
            <LockClosedIcon class="w-5 h-5 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input v-model="newPassword" type="password" class="input-modern pl-11" placeholder="至少6位" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">确认新密码</label>
          <div class="relative">
            <LockClosedIcon class="w-5 h-5 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input v-model="confirmPassword" type="password" class="input-modern pl-11" placeholder="再次输入新密码" @keydown.enter="resetPassword" />
          </div>
        </div>
        <button @click="resetPassword" :disabled="loading" class="w-full btn-primary py-3 text-base flex items-center justify-center space-x-2">
          <span>{{ loading ? '重置中...' : '重置密码' }}</span>
        </button>
      </div>

      <p v-if="error" class="text-red-500 text-sm text-center mt-4 shake">{{ error }}</p>
      <p v-if="success" class="text-green-600 text-sm text-center mt-4 fade-in-up">密码重置成功，请登录</p>

      <div class="mt-8 text-center text-sm text-gray-500">
        <router-link to="/login" class="text-indigo-600 hover:text-indigo-700 font-medium hover:underline flex items-center justify-center space-x-1">
          <ArrowLeftIcon class="w-4 h-4" />
          <span>返回登录</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api/axios'
import { UserIcon, KeyIcon, LockClosedIcon, ArrowRightIcon, ArrowLeftIcon, UserCircleIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const step = ref(1)
const username = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(false)

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
