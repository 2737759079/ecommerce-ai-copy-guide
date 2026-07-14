<template>
  <div class="space-y-6 fade-in-up">
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-800">商品评论</h2>
        <p class="text-sm text-gray-500 mt-1">洞察用户反馈，驱动商品优化</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <button @click="downloadTemplate" class="bg-white text-gray-700 border border-gray-200 px-3 py-2 rounded-xl text-sm hover:bg-page transition-colors">下载模板</button>
        <input type="file" @change="importReviews" accept=".xlsx,.xls" class="hidden" ref="importInput" />
        <button @click="$refs.importInput.click()" class="bg-accent-blue/30 text-blue-800 border border-accent-blue px-3 py-2 rounded-xl text-sm hover:bg-accent-blue/50 transition-colors">批量导入</button>
        <button @click="showForm = true" class="btn-primary text-sm flex items-center space-x-1">
          <PlusIcon class="w-4 h-4" />
          <span>添加评论</span>
        </button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="card rounded-2xl p-5 flex items-center space-x-4">
        <div class="w-12 h-12 rounded-xl bg-green-100 text-green-600 flex items-center justify-center"><FaceSmileIcon class="w-6 h-6" /></div>
        <div>
          <p class="text-sm text-gray-500">好评</p>
          <p class="text-2xl font-bold text-gradient">{{ stats.positive }}</p>
        </div>
      </div>
      <div class="card rounded-2xl p-5 flex items-center space-x-4">
        <div class="w-12 h-12 rounded-xl bg-yellow-100 text-yellow-600 flex items-center justify-center"><FaceFrownIcon class="w-6 h-6" /></div>
        <div>
          <p class="text-sm text-gray-500">中评</p>
          <p class="text-2xl font-bold text-gradient">{{ stats.neutral }}</p>
        </div>
      </div>
      <div class="card rounded-2xl p-5 flex items-center space-x-4">
        <div class="w-12 h-12 rounded-xl bg-red-100 text-red-600 flex items-center justify-center"><FaceMehIcon class="w-6 h-6" /></div>
        <div>
          <p class="text-sm text-gray-500">差评</p>
          <p class="text-2xl font-bold text-gradient">{{ stats.negative }}</p>
        </div>
      </div>
      <div class="card rounded-2xl p-5 flex items-center space-x-4">
        <div class="w-12 h-12 rounded-xl bg-primary-light text-primary flex items-center justify-center"><StarIcon class="w-6 h-6" /></div>
        <div>
          <p class="text-sm text-gray-500">平均评分</p>
          <p class="text-2xl font-bold text-gradient">{{ stats.avg_rating }}</p>
        </div>
      </div>
    </div>

    <!-- 筛选 -->
    <div class="card rounded-2xl p-5">
      <div class="flex flex-col md:flex-row gap-4 flex-wrap items-end">
        <FormSelect v-model="filter.productId" label="商品" :icon="CubeIcon" class="min-w-[180px]">
          <option value="">全部商品</option>
          <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
        </FormSelect>
        <FormInput v-model="filter.keyword" label="关键词" :icon="MagnifyingGlassIcon" placeholder="评论内容关键词" class="flex-1 min-w-[200px]" />
        <FormSelect v-model="filter.sentiment" label="情感" :icon="FaceSmileIcon" class="w-36">
          <option value="">全部情感</option>
          <option value="positive">好评</option>
          <option value="neutral">中评</option>
          <option value="negative">差评</option>
        </FormSelect>
        <FormSelect v-model="filter.status" label="商品状态" :icon="AdjustmentsHorizontalIcon" class="w-36">
          <option value="">全部状态</option>
          <option value="on">上架</option>
          <option value="off">下架</option>
          <option value="deleted">已删除</option>
        </FormSelect>
        <button @click="loadReviews" class="btn-primary text-sm flex items-center space-x-1">
          <MagnifyingGlassIcon class="w-4 h-4" />
          <span>搜索</span>
        </button>
      </div>
    </div>

    <!-- 评论列表 -->
    <div>
      <h3 class="font-bold text-lg text-gray-800 mb-4 flex items-center space-x-2">
        <ChatBubbleLeftRightIcon class="w-5 h-5 text-primary" />
        <span>评论列表</span>
        <span class="text-sm font-normal text-gray-500">({{ reviews.length }})</span>
      </h3>
      <div v-if="reviews.length === 0" class="text-center py-16 bg-white rounded-3xl shadow-card">
        <ChatBubbleLeftRightIcon class="w-12 h-12 mx-auto mb-3 text-primary/30" />
        <p class="text-gray-500">暂无评论</p>
      </div>
      <div v-else class="grid grid-cols-1 xl:grid-cols-2 gap-5">
        <div v-for="(r, idx) in reviews" :key="r.id" class="card card-hover rounded-2xl p-5 fade-in-up" :style="{ animationDelay: idx * 40 + 'ms' }">
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center space-x-3">
              <div class="w-12 h-12 rounded-xl bg-white border border-gray-100 flex items-center justify-center overflow-hidden flex-shrink-0">
                <img v-if="r.product_image" :src="normalizeImage(r.product_image)" class="w-full h-full object-cover" />
                <span v-else class="text-lg font-bold text-primary">{{ r.product_name?.charAt(0) }}</span>
              </div>
              <div>
                <p class="font-semibold text-gray-800 text-sm">{{ r.product_name }}</p>
                <p class="text-xs text-gray-400">{{ r.product_display_id }} · {{ statusText(r.product_status) }}</p>
              </div>
            </div>
            <span :class="sentimentClass(r.sentiment)" class="badge">{{ sentimentText(r.sentiment) }}</span>
          </div>

          <div class="flex items-center space-x-2 mb-2">
            <div class="w-7 h-7 rounded-full bg-gradient-to-br from-primary to-accent-blue flex items-center justify-center text-white text-xs font-bold">
              {{ (r.user_nickname || 'U').charAt(0).toUpperCase() }}
            </div>
            <span class="text-sm font-medium text-gray-700">{{ r.user_nickname || '匿名用户' }}</span>
            <span class="text-yellow-400 text-sm">{{ '★'.repeat(r.rating) }}{{ '☆'.repeat(5 - r.rating) }}</span>
          </div>

          <p class="text-sm text-gray-700 leading-relaxed mb-3">{{ r.content }}</p>

          <div v-if="r.images && r.images.length" class="flex flex-wrap gap-2 mb-3">
            <img v-for="(img, i) in r.images" :key="i" :src="normalizeImage(img)" class="w-16 h-16 object-cover rounded-lg border cursor-pointer hover:opacity-90" @click="previewImage = normalizeImage(img)" />
          </div>
          <video v-if="r.video_url" :src="normalizeImage(r.video_url)" controls class="h-32 rounded-lg mb-3"></video>

          <div class="flex items-center justify-between pt-3 border-t border-gray-100">
            <span class="text-xs text-gray-400">{{ new Date(r.created_at).toLocaleString() }} · {{ r.source === 'merchant' ? '商家添加' : '用户' }}</span>
            <button @click="confirmDelete(r)" class="text-xs text-red-500 hover:text-white hover:bg-red-500 px-3 py-1.5 rounded-lg transition-colors">删除</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 情感分析 -->
    <div class="card rounded-2xl p-6">
      <h3 class="font-bold text-lg text-gray-800 mb-4 flex items-center space-x-2">
        <ChartPieIcon class="w-5 h-5 text-primary" />
        <span>评论情感分析</span>
      </h3>
      <div class="flex flex-col md:flex-row gap-4 mb-4">
        <FormSelect v-model="analyzeProductId" label="分析商品" :icon="CubeIcon" placeholder="请选择商品" class="flex-1">
          <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
        </FormSelect>
        <button @click="analyzeProduct" class="btn-primary text-sm flex items-center space-x-1">
          <ChartPieIcon class="w-4 h-4" />
          <span>分析</span>
        </button>
      </div>
      <div v-if="analyzeResult" class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div class="bg-green-50 rounded-xl p-4"><p class="text-xs text-gray-500">好评</p><p class="text-2xl font-bold text-green-600">{{ analyzeResult.positive }}</p></div>
        <div class="bg-yellow-50 rounded-xl p-4"><p class="text-xs text-gray-500">中评</p><p class="text-2xl font-bold text-yellow-600">{{ analyzeResult.neutral }}</p></div>
        <div class="bg-red-50 rounded-xl p-4"><p class="text-xs text-gray-500">差评</p><p class="text-2xl font-bold text-red-600">{{ analyzeResult.negative }}</p></div>
        <div class="bg-primary-light rounded-xl p-4"><p class="text-xs text-gray-500">平均评分</p><p class="text-2xl font-bold text-primary">{{ analyzeResult.avg_rating }}</p></div>
      </div>
      <div v-if="analyzeResult?.positive_keywords?.length" class="mb-3">
        <p class="text-sm text-gray-600 mb-2">好评关键词</p>
        <div class="flex flex-wrap gap-2">
          <span v-for="kw in analyzeResult.positive_keywords" :key="kw" class="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs">{{ kw }}</span>
        </div>
      </div>
      <div v-if="analyzeResult?.negative_keywords?.length">
        <p class="text-sm text-gray-600 mb-2">差评关键词</p>
        <div class="flex flex-wrap gap-2">
          <span v-for="kw in analyzeResult.negative_keywords" :key="kw" class="bg-red-100 text-red-700 px-3 py-1 rounded-full text-xs">{{ kw }}</span>
        </div>
      </div>
    </div>

    <!-- 评论总结 -->
    <div class="card rounded-2xl p-6">
      <h3 class="font-bold text-lg text-gray-800 mb-4 flex items-center space-x-2">
        <SparklesIcon class="w-5 h-5 text-primary" />
        <span>评论总结与改进建议</span>
      </h3>
      <div class="flex flex-col md:flex-row gap-4 mb-4">
        <FormSelect v-model="summaryProductId" label="总结商品" :icon="CubeIcon" placeholder="请选择商品" class="flex-1">
          <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
        </FormSelect>
        <button @click="generateSummary" :disabled="summaryLoading" class="btn-primary text-sm flex items-center justify-center space-x-1 disabled:opacity-60">
          <svg v-if="summaryLoading" class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <SparklesIcon v-else class="w-4 h-4" />
          <span>{{ summaryLoading ? '生成中...' : '生成总结' }}</span>
        </button>
      </div>
      <div v-if="summaryResult" class="bg-page rounded-2xl p-5 border border-primary-light/50">
        <p class="font-semibold text-gray-800 mb-2">总结</p>
        <p class="text-sm text-gray-700 mb-4 whitespace-pre-wrap leading-relaxed">{{ summaryResult.summary }}</p>
        <p class="font-semibold text-gray-800 mb-2">改进建议</p>
        <ul class="list-disc list-inside text-sm text-gray-700 mb-4 space-y-1">
          <li v-for="(s, idx) in summaryResult.suggestions" :key="idx">{{ s }}</li>
        </ul>
        <div class="flex justify-end space-x-2">
          <button @click="exportSummary('txt')" class="px-3 py-1.5 border rounded-xl text-sm hover:bg-white transition-colors">导出TXT</button>
          <button @click="exportSummary('docx')" class="px-3 py-1.5 border rounded-xl text-sm hover:bg-white transition-colors">导出Word</button>
        </div>
      </div>
    </div>

    <!-- 添加评论弹窗 -->
    <div v-if="showForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md modal-in">
        <h3 class="font-bold text-lg mb-4 flex items-center space-x-2">
          <PlusIcon class="w-5 h-5 text-primary" />
          <span>添加评论</span>
        </h3>
        <div class="space-y-3">
          <FormSelect v-model="form.product_id" label="选择商品" :icon="CubeIcon" placeholder="请选择商品" class="w-full">
            <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
          </FormSelect>
          <FormSelect v-model="form.rating" label="评分" :icon="StarIcon" placeholder="请选择评分" class="w-full">
            <option v-for="n in 5" :key="n" :value="n">{{ n }}星</option>
          </FormSelect>
          <FormInput v-model="form.content" label="评论内容" :icon="ChatBubbleLeftRightIcon" type="textarea" :rows="3" placeholder="请输入评论内容" />
        </div>
        <div class="mt-6 flex justify-end space-x-2">
          <button @click="showForm = false" class="px-4 py-2 border rounded-xl hover:bg-page transition-colors text-sm">取消</button>
          <button @click="submitReview" class="px-4 py-2 bg-primary text-white rounded-xl hover:bg-primary-dark transition-colors text-sm">保存</button>
        </div>
      </div>
    </div>

    <!-- 删除确认 -->
    <div v-if="showConfirm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl p-6 w-80 modal-in">
        <h3 class="font-bold text-lg mb-4">确认删除</h3>
        <p class="text-sm text-gray-600 mb-4">确定删除该评论吗？</p>
        <div class="flex justify-end space-x-2">
          <button @click="showConfirm = false" class="px-4 py-2 border rounded-xl hover:bg-page transition-colors text-sm">取消</button>
          <button @click="doDelete" class="px-4 py-2 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-colors text-sm">确定</button>
        </div>
      </div>
    </div>

    <!-- 图片预览 -->
    <div v-if="previewImage" @click="previewImage = ''" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <img :src="previewImage" class="max-w-full max-h-full rounded-lg" />
    </div>

    <AppLoading v-if="summaryLoading" message="AI 正在生成评论总结，请稍候..." />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/axios'
import FormInput from '../../components/ui/FormInput.vue'
import FormSelect from '../../components/ui/FormSelect.vue'
import AppLoading from '../../components/AppLoading.vue'
import {
  CubeIcon,
  MagnifyingGlassIcon,
  FaceSmileIcon,
  FaceFrownIcon,
  FaceMehIcon,
  AdjustmentsHorizontalIcon,
  StarIcon,
  ChatBubbleLeftRightIcon,
  ChartPieIcon,
  SparklesIcon,
  PlusIcon,
  TrashIcon,
} from '@heroicons/vue/24/outline'

const baseUrl = 'http://127.0.0.1:8000'

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
const previewImage = ref('')

function statusText(status) {
  const map = { on: '上架', off: '下架', deleted: '已删除' }
  return map[status] || status
}

function sentimentText(s) {
  const map = { positive: '好评', neutral: '中评', negative: '差评' }
  return map[s] || s
}

function sentimentClass(s) {
  return s === 'positive' ? 'badge-green' : s === 'negative' ? 'badge-red' : 'badge-yellow'
}

function normalizeImage(url) {
  if (!url) return ''
  return url.startsWith('http') ? url : baseUrl + url
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
