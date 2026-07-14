<template>
  <div class="fade-in-up">
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-800">知识库管理</h2>
        <p class="text-sm text-gray-500 mt-1">共 {{ items.length }} 条知识 · 点击卡片可展开完整回答</p>
      </div>
      <div class="flex items-center flex-wrap gap-2">
        <FormSelect v-model="filter.productId" label="关联商品" :icon="CubeIcon" class="min-w-[160px]">
          <option value="">全部商品</option>
          <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
        </FormSelect>
        <button @click="loadData" class="bg-page text-primary border border-primary-light px-3 py-2 rounded-xl text-sm hover:bg-primary-light transition-colors">
          <MagnifyingGlassIcon class="w-4 h-4 inline" />
        </button>
        <button @click="showForm = true" class="btn-primary text-sm flex items-center space-x-1">
          <PlusIcon class="w-4 h-4" />
          <span>新增知识</span>
        </button>
        <button @click="downloadTemplate" class="bg-white text-gray-700 border border-gray-200 px-3 py-2 rounded-xl text-sm hover:bg-page transition-colors">下载模板</button>
        <button @click="exportKnowledge" class="bg-white text-green-600 border border-green-200 px-3 py-2 rounded-xl text-sm hover:bg-green-50 transition-colors">导出</button>
        <input type="file" @change="importKnowledge" accept=".xlsx,.xls" class="hidden" ref="importInput" />
        <button @click="$refs.importInput.click()" class="bg-accent-blue/30 text-blue-800 border border-accent-blue px-3 py-2 rounded-xl text-sm hover:bg-accent-blue/50 transition-colors">批量导入</button>
      </div>
    </div>

    <div v-if="items.length === 0" class="text-center py-20 bg-white rounded-3xl shadow-card">
      <div class="w-20 h-20 bg-primary-light rounded-full flex items-center justify-center mx-auto mb-4">
        <BookOpenIcon class="w-10 h-10 text-primary/60" />
      </div>
      <p class="text-gray-500">暂无知识条目</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
      <div
        v-for="(item, idx) in items"
        :key="item.id"
        class="card card-hover rounded-2xl p-5 fade-in-up flex flex-col"
        :style="{ animationDelay: idx * 50 + 'ms' }"
      >
        <div class="flex items-start justify-between mb-3">
          <span class="badge" :class="categoryClass(item.category)">{{ categoryText(item.category) }}</span>
          <span class="text-xs text-gray-400">{{ productName(item.product_id) }}</span>
        </div>
        <h3 class="font-bold text-gray-800 mb-2 line-clamp-2">{{ item.question }}</h3>
        <div class="flex-1">
          <p class="text-sm text-gray-600 leading-relaxed" :class="expandedIds.includes(item.id) ? '' : 'line-clamp-3'">{{ item.answer }}</p>
          <button
            v-if="item.answer.length > 80"
            @click="toggleExpand(item.id)"
            class="text-xs text-primary hover:text-primary-dark mt-1 font-medium"
          >
            {{ expandedIds.includes(item.id) ? '收起' : '展开' }}
          </button>
        </div>
        <div class="flex gap-2 mt-4 pt-4 border-t border-gray-100">
          <button @click="edit(item)" class="flex-1 py-2 rounded-xl bg-primary-light text-primary hover:bg-primary hover:text-white transition-colors text-sm font-medium flex items-center justify-center space-x-1">
            <PencilSquareIcon class="w-4 h-4" />
            <span>编辑</span>
          </button>
          <button @click="remove(item.id)" class="flex-1 py-2 rounded-xl bg-red-50 text-red-500 hover:bg-red-500 hover:text-white transition-colors text-sm font-medium flex items-center justify-center space-x-1">
            <TrashIcon class="w-4 h-4" />
            <span>删除</span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="showForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl p-6 w-full max-w-lg modal-in max-h-[90vh] overflow-y-auto">
        <h3 class="font-bold text-lg mb-4 flex items-center space-x-2">
          <BookOpenIcon class="w-5 h-5 text-primary" />
          <span>{{ editing ? '编辑知识' : '新增知识' }}</span>
        </h3>
        <div class="space-y-3">
          <FormSelect v-model="form.product_id" label="关联商品" :icon="CubeIcon">
            <option :value="null">通用</option>
            <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
          </FormSelect>
          <FormSelect v-model="form.category" label="分类" :icon="TagIcon">
            <option value="common">常见问题</option>
            <option value="size">尺码</option>
            <option value="material">材质</option>
            <option value="aftersale">售后</option>
            <option value="activity">活动</option>
          </FormSelect>
          <FormInput v-model="form.question" label="问题" :icon="ChatBubbleLeftRightIcon" placeholder="请输入问题" />
          <FormInput v-model="form.answer" label="回答" type="textarea" :rows="4" :icon="DocumentTextIcon" placeholder="请输入回答" />
        </div>
        <div class="mt-6 flex justify-end space-x-2">
          <button @click="showForm = false" class="px-4 py-2 border rounded-xl hover:bg-page transition-colors text-sm">取消</button>
          <button @click="save" class="px-4 py-2 bg-primary text-white rounded-xl hover:bg-primary-dark transition-colors text-sm">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/axios'
import FormInput from '../../components/ui/FormInput.vue'
import FormSelect from '../../components/ui/FormSelect.vue'
import {
  CubeIcon,
  TagIcon,
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  BookOpenIcon,
  PlusIcon,
  PencilSquareIcon,
  TrashIcon,
  MagnifyingGlassIcon,
} from '@heroicons/vue/24/outline'

const items = ref([])
const products = ref([])
const showForm = ref(false)
const editing = ref(false)
const form = ref({ product_id: null, category: 'common', question: '', answer: '' })
const filter = ref({ productId: '' })
const expandedIds = ref([])

const categoryMap = {
  common: { text: '常见问题', class: 'badge-purple' },
  size: { text: '尺码', class: 'badge-blue' },
  material: { text: '材质', class: 'badge-yellow' },
  aftersale: { text: '售后', class: 'badge-green' },
  activity: { text: '活动', class: 'badge-indigo' },
}

function categoryText(c) {
  return categoryMap[c]?.text || c
}

function categoryClass(c) {
  return categoryMap[c]?.class || 'badge-gray'
}

async function loadData() {
  const params = {}
  if (filter.value.productId) params.product_id = filter.value.productId
  const [i, p] = await Promise.all([api.get('/knowledge', { params }), api.get('/products', { params: { status: '' } })])
  items.value = i.data
  products.value = p.data
}

function productName(id) {
  const p = products.value.find(x => x.id === id)
  return p ? p.name : '通用'
}

function toggleExpand(id) {
  const idx = expandedIds.value.indexOf(id)
  if (idx >= 0) expandedIds.value.splice(idx, 1)
  else expandedIds.value.push(id)
}

function edit(item) {
  editing.value = true
  form.value = { ...item }
  showForm.value = true
}

async function save() {
  if (editing.value) {
    await api.put(`/knowledge/${form.value.id}`, form.value)
  } else {
    await api.post('/knowledge', form.value)
  }
  showForm.value = false
  editing.value = false
  form.value = { product_id: null, category: 'common', question: '', answer: '' }
  loadData()
}

async function remove(id) {
  if (!confirm('确定删除该知识条目吗？')) return
  await api.delete(`/knowledge/${id}`)
  loadData()
}

async function downloadTemplate() {
  const res = await api.get('/knowledge/template/download', { responseType: 'blob' })
  const url = URL.createObjectURL(new Blob([res.data]))
  const a = document.createElement('a')
  a.href = url
  a.download = 'knowledge_template.xlsx'
  a.click()
}

async function exportKnowledge() {
  const params = {}
  if (filter.value.productId) params.product_id = filter.value.productId
  const res = await api.get('/knowledge/export', { params, responseType: 'blob' })
  const url = URL.createObjectURL(new Blob([res.data]))
  const a = document.createElement('a')
  a.href = url
  a.download = 'knowledge_export.xlsx'
  a.click()
}

async function importKnowledge(e) {
  const file = e.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  await api.post('/knowledge/import', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  alert('导入成功')
  loadData()
}

onMounted(loadData)
</script>
