<template>
  <div class="fade-in-up">
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-800">商品管理</h2>
        <p class="text-sm text-gray-500 mt-1">共 {{ products.length }} 件商品 · 点击状态标签即可上下架</p>
      </div>
      <div class="flex items-center flex-wrap gap-2">
        <FormInput v-model="searchKeyword" label="搜索商品" @keyup.enter="loadProducts" placeholder="请输入商品名称" :icon="MagnifyingGlassIcon" class="min-w-[180px]" />
        <button @click="loadProducts" class="bg-page text-primary border border-primary-light px-3 py-2 rounded-xl text-sm hover:bg-primary-light transition-colors">
          <MagnifyingGlassIcon class="w-4 h-4 inline" />
        </button>
        <button @click="openCreate" class="btn-primary text-sm">新增商品</button>
        <button @click="downloadTemplate" class="bg-white text-gray-700 border border-gray-200 px-4 py-2 rounded-xl text-sm hover:bg-page transition-colors">下载模板</button>
        <button @click="exportProducts" class="bg-white text-green-600 border border-green-200 px-4 py-2 rounded-xl text-sm hover:bg-green-50 transition-colors">导出</button>
        <input type="file" @change="importProducts" accept=".xlsx,.xls,.json" class="hidden" ref="fileInput" />
        <button @click="$refs.fileInput.click()" class="bg-blue-50 text-blue-700 border border-blue-200 px-4 py-2 rounded-xl text-sm hover:bg-blue-100 transition-colors">导入</button>
      </div>
    </div>

    <div v-if="products.length === 0" class="text-center py-20 bg-white rounded-3xl shadow-card">
      <div class="w-20 h-20 bg-primary-light rounded-full flex items-center justify-center mx-auto mb-4">
        <CubeIcon class="w-10 h-10 text-primary/60" />
      </div>
      <p class="text-gray-500">暂无商品</p>
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
      <div
        v-for="(p, idx) in products"
        :key="p.id"
        class="card card-hover rounded-2xl overflow-hidden fade-in-up"
        :style="{ animationDelay: idx * 50 + 'ms' }"
      >
        <div class="relative h-44 bg-page overflow-hidden group">
          <img v-if="firstImage(p)" :src="firstImage(p)" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
          <div v-else class="w-full h-full flex flex-col items-center justify-center text-gray-400">
            <PhotoIcon class="w-12 h-12 mb-2 text-primary/30" />
            <span class="text-xs">暂无图片</span>
          </div>
          <div class="absolute top-3 left-3">
            <span class="badge" :class="statusBadgeClass(p.status)">{{ statusText(p.status) }}</span>
          </div>
        </div>
        <div class="p-4">
          <div class="flex justify-between items-start mb-2">
            <h3 class="font-bold text-gray-800 line-clamp-1">{{ p.name }}</h3>
            <span class="text-xs text-gray-400 font-mono">{{ p.display_id }}</span>
          </div>
          <p class="text-xs text-gray-500 mb-3">{{ p.category || '未分类' }}</p>
          <div class="flex items-baseline space-x-1 mb-3">
            <span class="text-xs text-gray-500">售价</span>
            <span class="text-xl font-bold text-gradient">¥{{ p.price }}</span>
          </div>
          <div class="flex items-center justify-between text-sm text-gray-600 mb-4">
            <span class="flex items-center space-x-1">
              <ArchiveBoxIcon class="w-4 h-4 text-primary/60" />
              <span>库存 {{ p.stock }}</span>
            </span>
            <span v-if="p.specs && p.specs.length" class="text-xs text-gray-400">{{ p.specs.length }} 种规格</span>
          </div>
          <div class="flex gap-2">
            <button
              @click="toggleStatus(p)"
              :class="p.status === 'on' ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200' : 'bg-green-100 text-green-700 hover:bg-green-200'"
              class="flex-1 py-2 rounded-xl text-sm font-medium transition-colors"
            >
              {{ p.status === 'on' ? '下架' : '上架' }}
            </button>
            <button @click="edit(p)" class="px-3 py-2 rounded-xl bg-primary-light text-primary hover:bg-primary hover:text-white transition-colors">
              <PencilSquareIcon class="w-4 h-4" />
            </button>
            <button @click="confirmRemove(p)" class="px-3 py-2 rounded-xl bg-red-50 text-red-500 hover:bg-red-500 hover:text-white transition-colors">
              <TrashIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto modal-in">
        <h3 class="font-bold text-lg mb-4 flex items-center space-x-2">
          <CubeIcon class="w-5 h-5 text-primary" />
          <span>{{ editing ? '编辑商品' : '新增商品' }}</span>
        </h3>
        <div class="space-y-3">
          <FormInput v-model="form.name" label="商品名称" :icon="CubeIcon" placeholder="请输入商品名称" />
          <FormInput v-model="form.category" label="商品分类" :icon="TagIcon" placeholder="请输入商品分类" />
          <FormInput v-model="form.description" label="商品描述" :icon="DocumentTextIcon" type="textarea" :rows="2" placeholder="请输入商品描述" />
          <div class="grid grid-cols-2 gap-3">
            <FormInput v-model.number="form.price" label="价格（元）" :icon="CurrencyYenIcon" type="number" min="0" step="0.01" placeholder="请填写商品售价，例如 99.00" />
            <FormInput v-model.number="form.stock" label="库存（件）" :icon="ArchiveBoxIcon" type="number" min="0" step="1" placeholder="请填写可售数量，例如 100" />
          </div>
          <FormInput v-model="specsText" label="商品规格" :icon="ListBulletIcon" placeholder="用逗号分隔，例如：红色,蓝色" />
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">商品图片</label>
            <input type="file" multiple accept="image/*" @change="handleImages" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary-light file:text-primary-dark hover:file:bg-primary-light/80" />
            <div class="flex flex-wrap gap-2 mt-2">
              <div v-for="(img, idx) in previewImages" :key="idx" class="relative w-16 h-16">
                <img :src="img" class="w-full h-full object-cover rounded-lg" />
                <button @click="removeImage(idx)" class="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-4 h-4 text-xs">×</button>
              </div>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">商品视频</label>
            <input type="file" accept="video/*" @change="handleVideo" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary-light file:text-primary-dark hover:file:bg-primary-light/80" />
            <video v-if="form.video_url && !videoFile" :src="baseUrl + form.video_url" controls class="mt-2 h-32 rounded-lg"></video>
          </div>
          <FormSelect v-model="form.status" label="商品状态" :icon="AdjustmentsHorizontalIcon">
            <option value="on">上架</option>
            <option value="off">下架</option>
          </FormSelect>
        </div>
        <div class="mt-6 flex justify-end space-x-2">
          <button @click="showForm = false" class="px-4 py-2 border rounded-xl hover:bg-page transition-colors">取消</button>
          <button @click="save" class="px-4 py-2 bg-primary text-white rounded-xl hover:bg-primary-dark transition-colors">保存</button>
        </div>
      </div>
    </div>

    <div v-if="showConfirm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-6 w-80 modal-in">
        <h3 class="font-bold text-lg mb-4">确认删除</h3>
        <p class="text-sm text-gray-600 mb-4">确定要删除商品 "{{ confirmItem?.name }}" 吗？</p>
        <div class="flex justify-end space-x-2">
          <button @click="showConfirm = false" class="px-4 py-2 border rounded-xl hover:bg-page transition-colors">取消</button>
          <button @click="doRemove" class="px-4 py-2 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-colors">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../api/axios'
import FormInput from '../../components/ui/FormInput.vue'
import FormSelect from '../../components/ui/FormSelect.vue'
import {
  MagnifyingGlassIcon,
  CubeIcon,
  TagIcon,
  DocumentTextIcon,
  CurrencyYenIcon,
  ArchiveBoxIcon,
  ListBulletIcon,
  AdjustmentsHorizontalIcon,
  PencilSquareIcon,
  TrashIcon,
  PhotoIcon,
} from '@heroicons/vue/24/outline'

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
  const map = { on: '上架中', off: '已下架', deleted: '已删除' }
  return map[status] || status
}

function statusBadgeClass(status) {
  return status === 'on' ? 'badge-green' : status === 'deleted' ? 'badge-red' : 'badge-gray'
}

function firstImage(product) {
  const images = product?.images || []
  const url = images[0] || ''
  if (!url) return ''
  return url.startsWith('http') ? url : baseUrl + url
}

async function loadProducts() {
  const res = await api.get('/products', { params: { status: '', keyword: searchKeyword.value } })
  products.value = res.data
}

async function toggleStatus(p) {
  const next = p.status === 'on' ? 'off' : 'on'
  const formData = new FormData()
  formData.append('status', next)
  await api.put(`/products/${p.id}`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  loadProducts()
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
