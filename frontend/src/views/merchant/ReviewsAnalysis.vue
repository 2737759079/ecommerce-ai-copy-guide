<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">商品评论</h2>
    <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
      <div class="flex flex-col md:flex-row gap-4 flex-wrap">
        <select v-model="filter.productId" class="border rounded-lg px-4 py-2">
          <option value="">全部商品</option>
          <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
        </select>
        <input v-model="filter.keyword" placeholder="搜索评论内容" class="border rounded-lg px-4 py-2 flex-1" />
        <select v-model="filter.sentiment" class="border rounded-lg px-4 py-2">
          <option value="">全部情感</option>
          <option value="positive">好评</option>
          <option value="neutral">中评</option>
          <option value="negative">差评</option>
        </select>
        <select v-model="filter.status" class="border rounded-lg px-4 py-2">
          <option value="">全部状态</option>
          <option value="on">上架</option>
          <option value="off">下架</option>
          <option value="deleted">已删除</option>
        </select>
        <button @click="loadReviews" class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700">搜索</button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
      <div class="bg-white rounded-xl shadow-sm p-6"><p class="text-sm text-gray-500">好评</p><p class="text-2xl font-bold text-green-600">{{ stats.positive }}</p></div>
      <div class="bg-white rounded-xl shadow-sm p-6"><p class="text-sm text-gray-500">中评</p><p class="text-2xl font-bold text-yellow-500">{{ stats.neutral }}</p></div>
      <div class="bg-white rounded-xl shadow-sm p-6"><p class="text-sm text-gray-500">差评</p><p class="text-2xl font-bold text-red-500">{{ stats.negative }}</p></div>
      <div class="bg-white rounded-xl shadow-sm p-6"><p class="text-sm text-gray-500">平均评分</p><p class="text-2xl font-bold text-indigo-600">{{ stats.avg_rating }}</p></div>
    </div>

    <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-bold text-lg">评论列表</h3>
        <div class="space-x-2">
          <button @click="downloadTemplate" class="bg-gray-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-gray-700">下载模板</button>
          <input type="file" @change="importReviews" accept=".xlsx,.xls" class="hidden" ref="importInput" />
          <button @click="$refs.importInput.click()" class="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-blue-700">批量导入</button>
          <button @click="showForm = true" class="bg-indigo-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-indigo-700">添加评论</button>
        </div>
      </div>
      <table class="w-full text-sm text-left">
        <thead class="bg-gray-50 text-gray-600">
          <tr>
            <th class="px-4 py-3">商品</th>
            <th>用户</th>
            <th>评分</th>
            <th>内容</th>
            <th>情感</th>
            <th>来源</th>
            <th>时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in reviews" :key="r.id" class="border-b hover:bg-gray-50">
            <td class="px-4 py-3">{{ r.product_name }}<br><span class="text-xs text-gray-400">{{ r.product_display_id }} / {{ statusText(r.product_status) }}</span></td>
            <td>{{ r.user_nickname }}<br><span class="text-xs text-gray-400">{{ r.user_display_id }}</span></td>
            <td><span class="text-yellow-500">{{ '★'.repeat(r.rating) }}{{ '☆'.repeat(5 - r.rating) }}</span></td>
            <td class="max-w-xs truncate">{{ r.content }}</td>
            <td><span :class="sentimentClass(r.sentiment)">{{ sentimentText(r.sentiment) }}</span></td>
            <td>{{ r.source === 'merchant' ? '商家添加' : '用户' }}</td>
            <td>{{ new Date(r.created_at).toLocaleString() }}</td>
            <td>
              <button @click="confirmDelete(r)" class="text-red-500 hover:underline">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="reviews.length === 0" class="p-6 text-center text-gray-500">暂无评论</div>
    </div>

    <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
      <h3 class="font-bold text-lg mb-4">评论情感分析</h3>
      <div class="flex flex-col md:flex-row gap-4">
        <select v-model="analyzeProductId" class="border rounded-lg px-4 py-2 flex-1">
          <option value="">选择商品</option>
          <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
        </select>
        <button @click="analyzeProduct" class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700">分析</button>
      </div>
      <div v-if="analyzeResult" class="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="bg-gray-50 rounded-lg p-4"><p class="text-sm text-gray-500">好评</p><p class="text-2xl font-bold text-green-600">{{ analyzeResult.positive }}</p></div>
        <div class="bg-gray-50 rounded-lg p-4"><p class="text-sm text-gray-500">中评</p><p class="text-2xl font-bold text-yellow-500">{{ analyzeResult.neutral }}</p></div>
        <div class="bg-gray-50 rounded-lg p-4"><p class="text-sm text-gray-500">差评</p><p class="text-2xl font-bold text-red-500">{{ analyzeResult.negative }}</p></div>
        <div class="bg-gray-50 rounded-lg p-4"><p class="text-sm text-gray-500">平均评分</p><p class="text-2xl font-bold text-indigo-600">{{ analyzeResult.avg_rating }}</p></div>
      </div>
      <div v-if="analyzeResult?.positive_keywords?.length" class="mt-4">
        <p class="text-sm text-gray-600 mb-2">好评关键词</p>
        <div class="flex flex-wrap gap-2">
          <span v-for="kw in analyzeResult.positive_keywords" :key="kw" class="bg-green-100 text-green-700 px-2 py-1 rounded text-xs">{{ kw }}</span>
        </div>
      </div>
      <div v-if="analyzeResult?.negative_keywords?.length" class="mt-4">
        <p class="text-sm text-gray-600 mb-2">差评关键词</p>
        <div class="flex flex-wrap gap-2">
          <span v-for="kw in analyzeResult.negative_keywords" :key="kw" class="bg-red-100 text-red-700 px-2 py-1 rounded text-xs">{{ kw }}</span>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
      <h3 class="font-bold text-lg mb-4">评论总结与改进建议</h3>
      <div class="flex flex-col md:flex-row gap-4 mb-4">
        <select v-model="summaryProductId" class="border rounded-lg px-4 py-2 flex-1">
          <option value="">选择商品</option>
          <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
        </select>
        <button @click="generateSummary" :disabled="summaryLoading" class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-60">{{ summaryLoading ? '生成中...' : '生成总结' }}</button>
      </div>
      <div v-if="summaryResult" class="bg-gray-50 p-4 rounded-lg">
        <p class="font-semibold mb-2">总结</p>
        <p class="text-sm text-gray-700 mb-4 whitespace-pre-wrap">{{ summaryResult.summary }}</p>
        <p class="font-semibold mb-2">改进建议</p>
        <ul class="list-disc list-inside text-sm text-gray-700 mb-4">
          <li v-for="(s, idx) in summaryResult.suggestions" :key="idx">{{ s }}</li>
        </ul>
        <div class="flex justify-end space-x-2">
          <button @click="exportSummary('txt')" class="px-3 py-1.5 border rounded-lg text-sm hover:bg-gray-50">导出TXT</button>
          <button @click="exportSummary('docx')" class="px-3 py-1.5 border rounded-lg text-sm hover:bg-gray-50">导出Word</button>
        </div>
      </div>
    </div>

    <div v-if="showForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-full max-w-md">
        <h3 class="font-bold text-lg mb-4">添加评论</h3>
        <div class="space-y-3">
          <select v-model="form.product_id" class="w-full border rounded-lg px-3 py-2">
            <option value="">选择商品</option>
            <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
          <select v-model="form.rating" class="w-full border rounded-lg px-3 py-2">
            <option v-for="n in 5" :key="n" :value="n">{{ n }}星</option>
          </select>
          <textarea v-model="form.content" placeholder="评论内容" rows="3" class="w-full border rounded-lg px-3 py-2"></textarea>
        </div>
        <div class="mt-6 flex justify-end space-x-2">
          <button @click="showForm = false" class="px-4 py-2 border rounded-lg">取消</button>
          <button @click="submitReview" class="px-4 py-2 bg-indigo-600 text-white rounded-lg">保存</button>
        </div>
      </div>
    </div>

    <div v-if="showConfirm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-80">
        <h3 class="font-bold text-lg mb-4">确认删除</h3>
        <p class="text-sm text-gray-600 mb-4">确定删除该评论吗？</p>
        <div class="flex justify-end space-x-2">
          <button @click="showConfirm = false" class="px-4 py-2 border rounded-lg">取消</button>
          <button @click="doDelete" class="px-4 py-2 bg-red-500 text-white rounded-lg">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/axios'

const products = ref([])
const reviews = ref([])
const stats = ref({ positive: 0, neutral: 0, negative: 0, avg_rating: 0 })
const filter = ref({ productId: '', keyword: '', sentiment: '', status: '' })
const analyzeProductId = ref('')
const analyzeResult = ref(null)
const summaryProductId = ref('')
const summaryResult = ref(null)
const summaryLoading = ref(false)
const showForm = ref(false)
const form = ref({ product_id: '', rating: 5, content: '' })
const showConfirm = ref(false)
const confirmItem = ref(null)

function statusText(status) {
  const map = { on: '上架', off: '下架', deleted: '已删除' }
  return map[status] || status
}

function sentimentText(s) {
  const map = { positive: '好评', neutral: '中评', negative: '差评' }
  return map[s] || s
}

function sentimentClass(s) {
  return s === 'positive' ? 'text-green-600' : s === 'negative' ? 'text-red-500' : 'text-yellow-500'
}

async function loadProducts() {
  const res = await api.get('/products', { params: { status: '', include_deleted: true } })
  products.value = res.data
}

async function loadReviews() {
  const params = {}
  if (filter.value.productId) params.product_id = filter.value.productId
  if (filter.value.keyword) params.keyword = filter.value.keyword
  if (filter.value.sentiment) params.sentiment = filter.value.sentiment
  if (filter.value.status) params.status = filter.value.status
  const res = await api.get('/reviews/merchant/list', { params })
  reviews.value = res.data
  calcStats(res.data)
}

function calcStats(list) {
  if (!list.length) {
    stats.value = { positive: 0, neutral: 0, negative: 0, avg_rating: 0 }
    return
  }
  const positive = list.filter(r => r.sentiment === 'positive').length
  const neutral = list.filter(r => r.sentiment === 'neutral').length
  const negative = list.filter(r => r.sentiment === 'negative').length
  const avg = (list.reduce((sum, r) => sum + r.rating, 0) / list.length).toFixed(1)
  stats.value = { positive, neutral, negative, avg_rating: avg }
}

async function analyzeProduct() {
  if (!analyzeProductId.value) return
  const res = await api.get(`/reviews/stats/${analyzeProductId.value}`)
  analyzeResult.value = res.data
}

async function generateSummary() {
  if (!summaryProductId.value) return
  summaryLoading.value = true
  try {
    const res = await api.post('/reviews/summary', { product_id: Number(summaryProductId.value) })
    summaryResult.value = res.data
  } catch (e) {
    alert(e.response?.data?.detail || '生成失败')
  } finally {
    summaryLoading.value = false
  }
}

async function exportSummary(fmt) {
  if (!summaryResult.value) return
  const content = `评论总结\n\n${summaryResult.value.summary}\n\n改进建议：\n${summaryResult.value.suggestions.map((s, i) => `${i + 1}. ${s}`).join('\n')}`
  const title = `${productName(Number(summaryProductId.value))}_评论总结`
  const res = await api.post('/reviews/summary/export', { format: fmt, content, title }, { responseType: 'blob' })
  const url = URL.createObjectURL(new Blob([res.data]))
  const a = document.createElement('a')
  a.href = url
  a.download = `${title}.${fmt}`
  a.click()
}

function productName(id) {
  const p = products.value.find(x => x.id === id)
  return p ? p.name : '商品'
}

async function submitReview() {
  await api.post('/reviews/merchant-create', form.value)
  showForm.value = false
  form.value = { product_id: '', rating: 5, content: '' }
  loadReviews()
}

function confirmDelete(r) {
  confirmItem.value = r
  showConfirm.value = true
}

async function doDelete() {
  if (!confirmItem.value) return
  await api.delete(`/reviews/${confirmItem.value.id}`)
  showConfirm.value = false
  confirmItem.value = null
  loadReviews()
}

async function downloadTemplate() {
  const res = await api.get('/reviews/template/download', { responseType: 'blob' })
  const url = URL.createObjectURL(new Blob([res.data]))
  const a = document.createElement('a')
  a.href = url
  a.download = 'reviews_template.xlsx'
  a.click()
}

async function importReviews(e) {
  const file = e.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  await api.post('/reviews/import', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  alert('导入成功')
  loadReviews()
}

onMounted(() => {
  loadProducts()
  loadReviews()
})
</script>
