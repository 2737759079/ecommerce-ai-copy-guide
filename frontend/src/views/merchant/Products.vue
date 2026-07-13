<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">商品管理</h2>
      <div class="flex items-center space-x-2">
        <input v-model="searchKeyword" @keyup.enter="loadProducts" placeholder="搜索商品名称" class="border rounded-lg px-3 py-2 text-sm" />
        <button @click="loadProducts" class="bg-gray-100 text-gray-700 px-3 py-2 rounded-lg text-sm hover:bg-gray-200">搜索</button>
        <button @click="openCreate" class="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700">新增商品</button>
        <button @click="downloadTemplate" class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700">下载模板</button>
        <button @click="exportProducts" class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">导出</button>
        <input type="file" @change="importProducts" accept=".xlsx,.xls,.json" class="hidden" ref="fileInput" />
        <button @click="$refs.fileInput.click()" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">导入</button>
      </div>
    </div>
    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm text-left">
        <thead class="bg-gray-50 text-gray-600">
          <tr>
            <th class="px-4 py-3">商品ID</th>
            <th>名称</th>
            <th>分类</th>
            <th>价格</th>
            <th>库存</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in products" :key="p.id" class="border-b hover:bg-gray-50">
            <td class="px-4 py-3">{{ p.display_id }}</td>
            <td>{{ p.name }}</td>
            <td>{{ p.category }}</td>
            <td>¥{{ p.price }}</td>
            <td>{{ p.stock }}</td>
            <td><span :class="p.status === 'on' ? 'text-green-600' : p.status === 'deleted' ? 'text-red-500' : 'text-gray-500'">{{ statusText(p.status) }}</span></td>
            <td class="space-x-2">
              <button @click="edit(p)" class="text-indigo-600 hover:underline">编辑</button>
              <button @click="confirmRemove(p)" class="text-red-500 hover:underline">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <h3 class="font-bold text-lg mb-4">{{ editing ? '编辑商品' : '新增商品' }}</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-sm text-gray-600 mb-1">商品名称</label>
            <input v-model="form.name" class="w-full border rounded-lg px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">分类</label>
            <input v-model="form.category" class="w-full border rounded-lg px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">描述</label>
            <textarea v-model="form.description" rows="2" class="w-full border rounded-lg px-3 py-2"></textarea>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm text-gray-600 mb-1">价格（单位：元，请填写商品售价）</label>
              <input v-model.number="form.price" type="number" min="0" step="0.01" placeholder="例如：99.00" class="w-full border rounded-lg px-3 py-2" />
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">库存（可售数量，请填写整数）</label>
              <input v-model.number="form.stock" type="number" min="0" step="1" placeholder="例如：100" class="w-full border rounded-lg px-3 py-2" />
            </div>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">规格（用逗号分隔）</label>
            <input v-model="specsText" class="w-full border rounded-lg px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">商品图片</label>
            <input type="file" multiple accept="image/*" @change="handleImages" class="w-full border rounded-lg px-3 py-2" />
            <div class="flex flex-wrap gap-2 mt-2">
              <div v-for="(img, idx) in previewImages" :key="idx" class="relative w-16 h-16">
                <img :src="img" class="w-full h-full object-cover rounded-lg" />
                <button @click="removeImage(idx)" class="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-4 h-4 text-xs">×</button>
              </div>
            </div>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">商品视频</label>
            <input type="file" accept="video/*" @change="handleVideo" class="w-full border rounded-lg px-3 py-2" />
            <video v-if="form.video_url && !videoFile" :src="baseUrl + form.video_url" controls class="mt-2 h-32 rounded-lg"></video>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">状态</label>
            <select v-model="form.status" class="w-full border rounded-lg px-3 py-2">
              <option value="on">上架</option>
              <option value="off">下架</option>
            </select>
          </div>
        </div>
        <div class="mt-6 flex justify-end space-x-2">
          <button @click="showForm = false" class="px-4 py-2 border rounded-lg">取消</button>
          <button @click="save" class="px-4 py-2 bg-indigo-600 text-white rounded-lg">保存</button>
        </div>
      </div>
    </div>

    <div v-if="showConfirm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-80">
        <h3 class="font-bold text-lg mb-4">确认删除</h3>
        <p class="text-sm text-gray-600 mb-4">确定要删除商品 "{{ confirmItem?.name }}" 吗？</p>
        <div class="flex justify-end space-x-2">
          <button @click="showConfirm = false" class="px-4 py-2 border rounded-lg">取消</button>
          <button @click="doRemove" class="px-4 py-2 bg-red-500 text-white rounded-lg">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../api/axios'

const route = useRoute()
const baseUrl = 'http://127.0.0.1:8000'
const products = ref([])
const showForm = ref(false)
const editing = ref(false)
const form = ref({ name: '', category: '', description: '', price: 0, stock: 0, specs: [], images: [], video_url: '', status: 'off' })
const specsText = ref('')
const imageFiles = ref([])
const previewImages = ref([])
const videoFile = ref(null)
const searchKeyword = ref('')
const showConfirm = ref(false)
const confirmItem = ref(null)

function statusText(status) {
  const map = { on: '上架', off: '下架', deleted: '已删除' }
  return map[status] || status
}

async function loadProducts() {
  const res = await api.get('/products', { params: { status: '', keyword: searchKeyword.value } })
  products.value = res.data
}

function openCreate() {
  editing.value = false
  form.value = { name: '', category: '', description: '', price: 0, stock: 0, specs: [], images: [], video_url: '', status: 'off' }
  specsText.value = ''
  imageFiles.value = []
  previewImages.value = []
  videoFile.value = null
  showForm.value = true
}

function edit(p) {
  editing.value = true
  form.value = { ...p }
  specsText.value = (p.specs || []).join(',')
  previewImages.value = (p.images || []).map(img => img.startsWith('http') ? img : baseUrl + img)
  imageFiles.value = []
  videoFile.value = null
  showForm.value = true
}

function handleImages(e) {
  const files = Array.from(e.target.files)
  imageFiles.value = files
  previewImages.value = files.map(f => URL.createObjectURL(f))
}

function removeImage(idx) {
  if (editing.value && form.value.images && form.value.images[idx]) {
    form.value.images.splice(idx, 1)
    previewImages.value.splice(idx, 1)
  } else if (imageFiles.value[idx]) {
    imageFiles.value.splice(idx, 1)
    previewImages.value.splice(idx, 1)
  }
}

function handleVideo(e) {
  videoFile.value = e.target.files[0]
}

async function save() {
  const formData = new FormData()
  formData.append('name', form.value.name)
  formData.append('category', form.value.category)
  formData.append('description', form.value.description)
  formData.append('price', form.value.price)
  formData.append('stock', form.value.stock)
  formData.append('status', form.value.status)
  formData.append('specs', specsText.value)

  if (editing.value) {
    formData.append('keep_images', (form.value.images || []).join(','))
  }
  imageFiles.value.forEach(f => formData.append('images', f))
  if (videoFile.value) {
    formData.append('video', videoFile.value)
  }

  if (editing.value) {
    await api.put(`/products/${form.value.id}`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  } else {
    await api.post('/products', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  }
  showForm.value = false
  editing.value = false
  form.value = { name: '', category: '', description: '', price: 0, stock: 0, specs: [], images: [], video_url: '', status: 'off' }
  specsText.value = ''
  imageFiles.value = []
  previewImages.value = []
  videoFile.value = null
  loadProducts()
}

function confirmRemove(p) {
  confirmItem.value = p
  showConfirm.value = true
}

async function doRemove() {
  if (!confirmItem.value) return
  await api.delete(`/products/${confirmItem.value.id}`)
  showConfirm.value = false
  confirmItem.value = null
  loadProducts()
}

async function exportProducts() {
  const res = await api.get('/products/export/data', { responseType: 'blob' })
  const url = URL.createObjectURL(new Blob([res.data]))
  const a = document.createElement('a')
  a.href = url
  a.download = 'products.xlsx'
  a.click()
}

async function downloadTemplate() {
  const res = await api.get('/products/template/download', { responseType: 'blob' })
  const url = URL.createObjectURL(new Blob([res.data]))
  const a = document.createElement('a')
  a.href = url
  a.download = 'product_template.xlsx'
  a.click()
}

async function importProducts(e) {
  const file = e.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  await api.post('/products/import', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  alert('导入成功')
  loadProducts()
}

onMounted(() => {
  loadProducts().then(() => {
    if (route.query.autoOpenCreate === '1') {
      openCreate()
      if (route.query.name) form.value.name = route.query.name
      if (route.query.category) form.value.category = route.query.category
      if (route.query.description) form.value.description = route.query.description
    }
  })
})
</script>
