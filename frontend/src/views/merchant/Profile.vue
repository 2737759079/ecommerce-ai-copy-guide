<template>
  <div class="max-w-4xl mx-auto space-y-6 fade-in-up">
    <!-- 个人信息 -->
    <div class="bg-white rounded-3xl shadow-lg p-6 md:p-8">
      <div class="flex flex-col sm:flex-row items-center sm:items-start space-y-4 sm:space-y-0 sm:space-x-6 mb-6">
        <div class="relative">
          <div class="w-24 h-24 rounded-full bg-gradient-to-br from-primary to-accent-blue p-1">
            <div class="w-full h-full rounded-full bg-white overflow-hidden flex items-center justify-center">
              <img v-if="user.avatar_url" :src="baseUrl + user.avatar_url" class="w-full h-full object-cover" />
              <span v-else class="text-2xl font-bold text-primary">{{ (user.nickname || user.username || 'M').charAt(0).toUpperCase() }}</span>
            </div>
          </div>
          <label class="absolute bottom-0 right-0 w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center cursor-pointer hover:bg-primary-dark transition-colors shadow-lg">
            <CameraIcon class="w-4 h-4" />
            <input type="file" accept="image/*" @change="uploadAvatar" class="hidden" />
          </label>
        </div>
        <div class="flex-1 text-center sm:text-left">
          <h2 class="text-2xl font-bold text-gray-800">{{ user.nickname || user.username }}</h2>
          <p class="text-sm text-gray-500 mt-1">管理员ID：{{ user.display_id }}</p>
          <p class="text-xs text-gray-400 mt-1">注册时间：{{ new Date(user.created_at).toLocaleDateString() }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <FormInput v-model="user.display_id" label="管理员ID" disabled :icon="IdentificationIcon" input-class="bg-gray-50" />
        <FormInput v-model="user.username" label="账号" disabled :icon="UserIcon" input-class="bg-gray-50" />
        <FormInput v-model="user.nickname" label="昵称" disabled :icon="UserIcon" input-class="bg-gray-50" />
        <FormInput :model-value="roleText" label="角色" disabled :icon="ShieldCheckIcon" input-class="bg-gray-50" />
      </div>
    </div>

    <!-- 修改密码 -->
    <div class="bg-white rounded-3xl shadow-lg p-6 md:p-8">
      <div class="flex items-center space-x-2 mb-5">
        <KeyIcon class="w-5 h-5 text-primary" />
        <h2 class="text-xl font-bold text-gray-800">修改密码</h2>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <FormInput v-model="pwdForm.old_password" label="原密码" type="password" placeholder="请输入原密码" :icon="LockClosedIcon" />
        <FormInput v-model="pwdForm.new_password" label="新密码" type="password" placeholder="请输入新密码" :icon="LockClosedIcon" />
        <FormInput v-model="pwdForm.confirm_password" label="确认新密码" type="password" placeholder="请再次输入新密码" :icon="LockClosedIcon" />
        <button @click="changePassword" class="btn-primary flex items-center justify-center space-x-2">
          <ArrowPathIcon class="w-4 h-4" />
          <span>修改密码</span>
        </button>
      </div>
      <p v-if="pwdError" class="text-red-500 text-sm mt-3 shake">{{ pwdError }}</p>
      <p v-if="pwdSuccess" class="text-green-600 text-sm mt-3 fade-in-up flex items-center space-x-1">
        <CheckCircleIcon class="w-4 h-4" />
        <span>密码修改成功</span>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import api from '../../api/axios'
import FormInput from '../../components/ui/FormInput.vue'
import {
  CameraIcon,
  IdentificationIcon,
  UserIcon,
  ShieldCheckIcon,
  KeyIcon,
  LockClosedIcon,
  ArrowPathIcon,
  CheckCircleIcon,
} from '@heroicons/vue/24/outline'

const baseUrl = 'http://127.0.0.1:8000'
const auth = useAuthStore()
const user = ref({ ...auth.user })

const pwdForm = ref({ old_password: '', new_password: '', confirm_password: '' })
const pwdError = ref('')
const pwdSuccess = ref(false)

const roleText = computed(() => {
  const map = { merchant: '商家管理员', user: '普通用户' }
  return map[user.value.role] || user.value.role
})

async function loadUser() {
  await auth.fetchUser()
  user.value = { ...auth.user }
}

async function uploadAvatar(e) {
  const file = e.target.files[0]
  if (!file) return
  if (!file.type.startsWith('image/')) {
    alert('请上传图片文件')
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    alert('图片大小不能超过 5MB')
    return
  }
  const formData = new FormData()
  formData.append('file', file)
  const res = await api.post('/auth/upload-avatar', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  user.value = res.data
  auth.user = res.data
}

async function changePassword() {
  pwdError.value = ''
  pwdSuccess.value = false
  if (!pwdForm.value.old_password || !pwdForm.value.new_password) {
    pwdError.value = '请填写原密码和新密码'
    return
  }
  if (pwdForm.value.new_password !== pwdForm.value.confirm_password) {
    pwdError.value = '两次新密码不一致'
    return
  }
  if (pwdForm.value.new_password.length < 6) {
    pwdError.value = '新密码至少6位'
    return
  }
  try {
    await api.post('/auth/change-password', pwdForm.value)
    pwdSuccess.value = true
    pwdForm.value = { old_password: '', new_password: '', confirm_password: '' }
  } catch (e) {
    pwdError.value = e.response?.data?.detail || '修改失败'
  }
}

onMounted(loadUser)
</script>
