<template>
  <div class="max-w-4xl mx-auto space-y-6 fade-in-up">
    <!-- 个人信息 -->
    <div class="bg-white rounded-3xl shadow-lg p-6 md:p-8">
      <div class="flex flex-col sm:flex-row items-center sm:items-start space-y-4 sm:space-y-0 sm:space-x-6 mb-6">
        <div class="relative">
          <div class="w-24 h-24 rounded-full bg-gradient-to-br from-indigo-500 to-pink-500 p-1">
            <div class="w-full h-full rounded-full bg-white overflow-hidden flex items-center justify-center">
              <img v-if="user.avatar_url" :src="baseUrl + user.avatar_url" class="w-full h-full object-cover" />
              <span v-else class="text-2xl font-bold text-indigo-600">{{ (user.nickname || 'U').charAt(0).toUpperCase() }}</span>
            </div>
          </div>
          <label class="absolute bottom-0 right-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center cursor-pointer hover:bg-indigo-700 transition-colors shadow-lg">
            <CameraIcon class="w-4 h-4" />
            <input type="file" accept="image/*" @change="uploadAvatar" class="hidden" />
          </label>
        </div>
        <div class="flex-1 text-center sm:text-left">
          <h2 class="text-2xl font-bold text-gray-800">{{ user.nickname }}</h2>
          <p class="text-sm text-gray-500 mt-1">用户ID：{{ user.display_id }}</p>
          <p class="text-xs text-gray-400 mt-1">注册时间：{{ new Date(user.created_at).toLocaleDateString() }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">用户ID</label>
          <div class="relative">
            <IdentificationIcon class="w-5 h-5 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input v-model="user.display_id" disabled class="input-modern pl-11 bg-gray-50" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">昵称</label>
          <div class="relative">
            <UserIcon class="w-5 h-5 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input v-model="user.nickname" disabled class="input-modern pl-11 bg-gray-50" />
          </div>
        </div>
      </div>
    </div>

    <!-- 修改密码 -->
    <div class="bg-white rounded-3xl shadow-lg p-6 md:p-8">
      <div class="flex items-center space-x-2 mb-5">
        <KeyIcon class="w-5 h-5 text-indigo-600" />
        <h2 class="text-xl font-bold text-gray-800">修改密码</h2>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="relative">
          <LockClosedIcon class="w-5 h-5 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input v-model="pwdForm.old_password" type="password" placeholder="原密码" class="input-modern pl-11" />
        </div>
        <div class="relative">
          <LockClosedIcon class="w-5 h-5 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input v-model="pwdForm.new_password" type="password" placeholder="新密码" class="input-modern pl-11" />
        </div>
        <div class="relative">
          <LockClosedIcon class="w-5 h-5 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input v-model="pwdForm.confirm_password" type="password" placeholder="确认新密码" class="input-modern pl-11" />
        </div>
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

    <!-- 常用地址 -->
    <div class="bg-white rounded-3xl shadow-lg p-6 md:p-8">
      <div class="flex justify-between items-center mb-5">
        <div class="flex items-center space-x-2">
          <MapPinIcon class="w-5 h-5 text-indigo-600" />
          <h2 class="text-xl font-bold text-gray-800">常用地址</h2>
        </div>
        <button @click="openAddressForm" class="btn-primary text-sm flex items-center space-x-1">
          <PlusIcon class="w-4 h-4" />
          <span>新增地址</span>
        </button>
      </div>
      <div v-if="addresses.length === 0" class="text-gray-500 text-sm text-center py-10 bg-gray-50 rounded-2xl">暂无地址</div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div v-for="addr in addresses" :key="addr.id" class="border border-gray-100 rounded-2xl p-4 hover:shadow-md transition-shadow bg-gray-50/50">
          <div class="flex justify-between items-start mb-2">
            <div class="flex items-center space-x-2">
              <span class="font-medium text-gray-800">{{ addr.name }}</span>
              <span class="text-sm text-gray-500">{{ addr.phone }}</span>
              <span v-if="addr.is_default" class="text-xs bg-indigo-100 text-indigo-600 px-2 py-0.5 rounded-full">默认</span>
            </div>
            <div class="flex items-center space-x-1">
              <button @click="editAddress(addr)" class="p-1.5 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors">
                <PencilSquareIcon class="w-4 h-4" />
              </button>
              <button @click="deleteAddress(addr.id)" class="p-1.5 text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                <TrashIcon class="w-4 h-4" />
              </button>
            </div>
          </div>
          <p class="text-sm text-gray-600">{{ addr.detail }}</p>
        </div>
      </div>
    </div>

    <!-- 我的收藏 -->
    <div class="bg-white rounded-3xl shadow-lg p-6 md:p-8">
      <div class="flex items-center space-x-2 mb-5">
        <HeartIcon class="w-5 h-5 text-red-500" />
        <h2 class="text-xl font-bold text-gray-800">我的收藏</h2>
      </div>
      <div v-if="favorites.length === 0" class="text-gray-500 text-sm text-center py-10 bg-gray-50 rounded-2xl">暂无收藏</div>
      <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div v-for="f in favorites" :key="f.id" @click="$router.push(`/product/${f.product_id}`)" class="bg-gray-50 rounded-xl p-4 cursor-pointer hover:shadow-md hover:-translate-y-1 transition-all text-center">
          <div class="w-10 h-10 mx-auto bg-gradient-to-br from-indigo-500 to-pink-500 rounded-full flex items-center justify-center text-white text-sm font-bold mb-2">
            {{ f.product_id }}
          </div>
          <p class="text-sm font-medium text-gray-700">商品ID：{{ f.product_id }}</p>
        </div>
      </div>
    </div>

    <!-- 浏览记录 -->
    <div class="bg-white rounded-3xl shadow-lg p-6 md:p-8">
      <div class="flex items-center space-x-2 mb-5">
        <ClockIcon class="w-5 h-5 text-indigo-600" />
        <h2 class="text-xl font-bold text-gray-800">浏览记录</h2>
      </div>
      <div v-if="history.length === 0" class="text-gray-500 text-sm text-center py-10 bg-gray-50 rounded-2xl">暂无记录</div>
      <div v-else class="space-y-2">
        <div v-for="h in history" :key="h.id" @click="$router.push(`/product/${h.product.id}`)" class="flex justify-between items-center text-sm border-b last:border-0 pb-3 last:pb-0 cursor-pointer hover:bg-gray-50 p-3 rounded-xl transition-colors">
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-indigo-50 rounded-lg flex items-center justify-center text-indigo-600 text-xs font-bold">
              {{ (h.product.ai_title || h.product.name).charAt(0) }}
            </div>
            <span class="text-gray-700 font-medium">{{ h.product.ai_title || h.product.name }}</span>
          </div>
          <span class="text-gray-400 text-xs">{{ new Date(h.created_at).toLocaleString() }}</span>
        </div>
      </div>
    </div>

    <!-- 地址弹窗 -->
    <div v-if="showAddressForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md modal-in">
        <h3 class="font-bold text-lg mb-4 flex items-center space-x-2">
          <MapPinIcon class="w-5 h-5 text-indigo-600" />
          <span>{{ addressEditing ? '编辑地址' : '新增地址' }}</span>
        </h3>
        <div class="space-y-3">
          <input v-model="addressForm.name" placeholder="收件人" class="input-modern" />
          <input v-model="addressForm.phone" placeholder="手机号" class="input-modern" />
          <textarea v-model="addressForm.detail" placeholder="详细地址" rows="2" class="input-modern"></textarea>
          <label class="flex items-center space-x-2 text-sm cursor-pointer">
            <input v-model="addressForm.is_default" type="checkbox" class="w-4 h-4 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500" />
            <span>设为默认地址</span>
          </label>
        </div>
        <div class="mt-6 flex justify-end space-x-2">
          <button @click="showAddressForm = false" class="btn-secondary text-sm">取消</button>
          <button @click="saveAddress" class="btn-primary text-sm">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import api from '../../api/axios'
import {
  CameraIcon,
  IdentificationIcon,
  UserIcon,
  KeyIcon,
  LockClosedIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  MapPinIcon,
  PlusIcon,
  PencilSquareIcon,
  TrashIcon,
  HeartIcon,
  ClockIcon,
} from '@heroicons/vue/24/outline'

const baseUrl = 'http://127.0.0.1:8000'
const auth = useAuthStore()
const user = ref({ ...auth.user })
const favorites = ref([])
const history = ref([])
const addresses = ref([])

const pwdForm = ref({ old_password: '', new_password: '', confirm_password: '' })
const pwdError = ref('')
const pwdSuccess = ref(false)

const showAddressForm = ref(false)
const addressEditing = ref(false)
const addressForm = ref({ id: null, name: '', phone: '', detail: '', is_default: false })

async function loadData() {
  await auth.fetchUser()
  user.value = { ...auth.user }
  const favRes = await api.get('/products/my/favorites')
  favorites.value = favRes.data
  const hisRes = await api.get('/products/my/browse-history')
  history.value = hisRes.data
  const addrRes = await api.get('/addresses')
  addresses.value = addrRes.data
}

async function uploadAvatar(e) {
  const file = e.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  const res = await api.post('/auth/upload-avatar', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  user.value = res.data
  auth.user = res.data
}

async function changePassword() {
  pwdError.value = ''
  pwdSuccess.value = false
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

function openAddressForm() {
  addressEditing.value = false
  addressForm.value = { id: null, name: '', phone: '', detail: '', is_default: false }
  showAddressForm.value = true
}

function editAddress(addr) {
  addressEditing.value = true
  addressForm.value = { ...addr }
  showAddressForm.value = true
}

async function saveAddress() {
  if (addressEditing.value) {
    await api.put(`/addresses/${addressForm.value.id}`, addressForm.value)
  } else {
    await api.post('/addresses', addressForm.value)
  }
  showAddressForm.value = false
  loadData()
}

async function deleteAddress(id) {
  if (!confirm('确定删除该地址吗？')) return
  await api.delete(`/addresses/${id}`)
  loadData()
}

onMounted(loadData)
</script>
