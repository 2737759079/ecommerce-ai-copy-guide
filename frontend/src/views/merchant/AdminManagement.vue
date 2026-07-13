<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">管理员管理</h2>
    <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
      <h3 class="font-bold text-lg mb-4">{{ editingId ? '编辑管理员' : '新增管理员' }}</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm text-gray-600 mb-1">账号</label>
          <input v-model="form.username" :disabled="!!editingId" type="text" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="请输入账号" />
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1">昵称</label>
          <input v-model="form.nickname" type="text" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="请输入昵称" />
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1">密码{{ editingId ? '（留空则不修改）' : '' }}</label>
          <input v-model="form.password" type="password" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="请输入密码" />
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1">确认密码{{ editingId ? '（留空则不修改）' : '' }}</label>
          <input v-model="form.confirm_password" type="password" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="再次输入密码" />
        </div>
      </div>
      <div class="mt-4 flex space-x-3">
        <button @click="save" :disabled="saving" class="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-60">
          {{ saving ? '保存中...' : '保存' }}
        </button>
        <button v-if="editingId" @click="resetForm" class="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300">取消</button>
      </div>
      <p v-if="error" class="text-red-500 text-sm mt-3">{{ error }}</p>
    </div>

    <div class="bg-white rounded-xl shadow-sm p-4 mb-6 flex gap-4">
      <input v-model="searchKeyword" placeholder="搜索账号/昵称/ID" class="border rounded-lg px-3 py-2 text-sm flex-1" />
      <button @click="load" class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700">搜索</button>
    </div>

    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm text-left">
        <thead class="bg-gray-50 text-gray-600">
          <tr>
            <th class="px-4 py-3">ID</th>
            <th>账号</th>
            <th>昵称</th>
            <th>角色</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="admin in admins" :key="admin.id" class="border-b hover:bg-gray-50">
            <td class="px-4 py-3">{{ admin.display_id }}</td>
            <td>{{ admin.username }}</td>
            <td>{{ admin.nickname }}</td>
            <td>{{ admin.role === 'merchant' ? '管理员' : admin.role }}</td>
            <td>{{ new Date(admin.created_at).toLocaleString() }}</td>
            <td>
              <button @click="edit(admin)" class="text-indigo-600 hover:underline mr-3">编辑</button>
              <button @click="note(admin)" class="text-blue-600 hover:underline mr-3">备注</button>
              <button @click="remove(admin)" :disabled="admin.id === currentUserId" :class="admin.id === currentUserId ? 'text-gray-400 cursor-not-allowed' : 'text-red-600 hover:underline'">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="admins.length === 0" class="p-6 text-center text-gray-500">暂无管理员数据</div>
    </div>

    <div v-if="showNote" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-full max-w-md">
        <h3 class="font-bold text-lg mb-4">备注：{{ noteAdmin?.nickname }}</h3>
        <textarea v-model="noteText" rows="4" class="w-full border rounded-lg px-3 py-2" placeholder="仅本人可见"></textarea>
        <div class="mt-6 flex justify-end space-x-2">
          <button @click="showNote = false" class="px-4 py-2 border rounded-lg">取消</button>
          <button @click="saveNote" class="px-4 py-2 bg-indigo-600 text-white rounded-lg">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../../api/axios'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const currentUserId = computed(() => auth.user?.id)

const admins = ref([])
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const editingId = ref(null)
const form = ref({ username: '', nickname: '', password: '', confirm_password: '' })
const searchKeyword = ref('')
const showNote = ref(false)
const noteAdmin = ref(null)
const noteText = ref('')

async function load() {
  loading.value = true
  try {
    const res = await api.get('/users/admins/list', { params: { keyword: searchKeyword.value } })
    admins.value = res.data
  } catch (e) {
    error.value = e.response?.data?.detail || '加载失败'
  } finally {
    loading.value = false
  }
}

function resetForm() {
  editingId.value = null
  form.value = { username: '', nickname: '', password: '', confirm_password: '' }
  error.value = ''
}

function edit(admin) {
  editingId.value = admin.id
  form.value = { username: admin.username, nickname: admin.nickname || '', password: '', confirm_password: '' }
  error.value = ''
}

async function save() {
  if (!editingId.value && (!form.value.username || !form.value.password)) {
    error.value = '请填写账号和密码'
    return
  }
  if (form.value.password) {
    if (form.value.password.length < 6) {
      error.value = '密码长度不能少于6位'
      return
    }
    if (form.value.password !== form.value.confirm_password) {
      error.value = '两次密码不一致'
      return
    }
  }
  saving.value = true
  error.value = ''
  try {
    if (editingId.value) {
      const payload = {}
      if (form.value.nickname !== undefined) payload.nickname = form.value.nickname
      if (form.value.password) payload.password = form.value.password
      await api.put(`/users/admins/${editingId.value}`, payload)
    } else {
      await api.post('/users/admins', {
        username: form.value.username,
        nickname: form.value.nickname,
        password: form.value.password,
      })
    }
    resetForm()
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}

async function note(admin) {
  noteAdmin.value = admin
  showNote.value = true
  noteText.value = ''
  try {
    const res = await api.get(`/users/admins/${admin.id}/note`)
    noteText.value = res.data.note
  } catch (e) {
    noteText.value = ''
  }
}

async function saveNote() {
  await api.post(`/users/admins/${noteAdmin.value.id}/note`, { note: noteText.value })
  showNote.value = false
  noteAdmin.value = null
  noteText.value = ''
}

async function remove(admin) {
  if (admin.id === currentUserId.value) {
    alert('不能删除当前登录的管理员账号')
    return
  }
  if (!confirm(`确定删除管理员 "${admin.username}" 吗？`)) return
  try {
    await api.delete(`/users/admins/${admin.id}`)
    await load()
  } catch (e) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

onMounted(() => {
  load()
  if (!auth.user) auth.fetchUser()
})
</script>
