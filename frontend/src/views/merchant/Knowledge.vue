<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">知识库管理</h2>
      <div class="space-x-2">
        <button @click="downloadTemplate" class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700">下载模板</button>
        <input type="file" @change="importKnowledge" accept=".xlsx,.xls" class="hidden" ref="importInput" />
        <button @click="$refs.importInput.click()" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">批量导入</button>
        <button @click="showForm = true" class="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700">新增知识</button>
      </div>
    </div>
    <div class="bg-white rounded-xl shadow-sm p-4 mb-6 flex gap-4 flex-wrap items-center">
      <select v-model="filter.productId" class="border rounded-lg px-3 py-2 text-sm">
        <option value="">全部商品</option>
        <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
      </select>
      <button @click="loadData" class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700">筛选</button>
      <button @click="exportKnowledge" class="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700">导出Excel</button>
    </div>
    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm text-left">
        <thead class="bg-gray-50 text-gray-600">
          <tr><th class="px-4 py-3">ID</th><th>商品</th><th>分类</th><th>问题</th><th>回答</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id" class="border-b hover:bg-gray-50">
            <td class="px-4 py-3">{{ item.id }}</td>
            <td>{{ productName(item.product_id) }}</td>
            <td>{{ item.category }}</td>
            <td class="truncate max-w-xs">{{ item.question }}</td>
            <td class="truncate max-w-xs">{{ item.answer }}</td>
            <td class="space-x-2">
              <button @click="edit(item)" class="text-indigo-600 hover:underline">编辑</button>
              <button @click="remove(item.id)" class="text-red-500 hover:underline">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-full max-w-lg">
        <h3 class="font-bold text-lg mb-4">{{ editing ? '编辑知识' : '新增知识' }}</h3>
        <div class="space-y-3">
          <select v-model="form.product_id" class="w-full border rounded-lg px-3 py-2">
            <option :value="null">通用</option>
            <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
          <select v-model="form.category" class="w-full border rounded-lg px-3 py-2">
            <option value="common">常见问题</option>
            <option value="size">尺码</option>
            <option value="material">材质</option>
            <option value="aftersale">售后</option>
            <option value="activity">活动</option>
          </select>
          <input v-model="form.question" placeholder="问题" class="w-full border rounded-lg px-3 py-2" />
          <textarea v-model="form.answer" placeholder="回答" rows="3" class="w-full border rounded-lg px-3 py-2"></textarea>
        </div>
        <div class="mt-6 flex justify-end space-x-2">
          <button @click="showForm = false" class="px-4 py-2 border rounded-lg">取消</button>
          <button @click="save" class="px-4 py-2 bg-indigo-600 text-white rounded-lg">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/axios'

const items = ref([])
const products = ref([])
const showForm = ref(false)
const editing = ref(false)
const form = ref({ product_id: null, category: 'common', question: '', answer: '' })
const filter = ref({ productId: '' })

async function loadData() {
  const params = {}
  if (filter.value.productId) params.product_id = filter.value.productId
  const [i, p] = await Promise.all([api.get('/knowledge', { params }), api.get('/products?status=')])
  items.value = i.data
  products.value = p.data
}

function productName(id) {
  const p = products.value.find(x => x.id === id)
  return p ? p.name : '通用'
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
  if (!confirm('确定删除？')) return
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
