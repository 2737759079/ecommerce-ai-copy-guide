<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">直播/短视频脚本生成</h2>
    <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
      <div class="flex flex-col md:flex-row gap-4">
        <select v-model="productId" class="border rounded-lg px-4 py-2 flex-1">
          <option value="">请选择商品</option>
          <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
        </select>
        <select v-model="style" class="border rounded-lg px-4 py-2">
          <option value="professional">专业</option>
          <option value="concise">简洁</option>
          <option value="premium">高端</option>
          <option value="lively">活泼</option>
          <option value="promotional">促销</option>
          <option value="lifestyle">生活化</option>
        </select>
        <select v-model="platform" class="border rounded-lg px-4 py-2">
          <option value="live">直播脚本</option>
          <option value="short">短视频脚本</option>
        </select>
        <button @click="generate" :disabled="!productId || loading" class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-60">生成脚本</button>
      </div>
      <p v-if="error" class="text-red-500 text-sm mt-3">{{ error }}</p>
    </div>
    <div v-if="result" class="bg-white rounded-xl shadow-sm p-6">
      <div class="flex justify-between items-center mb-3">
        <h3 class="font-bold text-lg">生成结果</h3>
        <div class="space-x-2">
          <button @click="exportFile('txt')" class="px-3 py-1.5 border rounded-lg text-sm hover:bg-gray-50">导出TXT</button>
          <button @click="exportFile('docx')" class="px-3 py-1.5 border rounded-lg text-sm hover:bg-gray-50">导出Word</button>
          <button @click="copy" class="px-3 py-1.5 border rounded-lg text-sm hover:bg-gray-50">复制</button>
        </div>
      </div>
      <div class="prose max-w-none bg-gray-50 p-4 rounded-lg text-sm text-gray-700" v-html="renderedMarkdown"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import api from '../../api/axios'

const products = ref([])
const productId = ref('')
const style = ref('professional')
const platform = ref('live')
const result = ref(null)
const loading = ref(false)
const error = ref('')

const renderedMarkdown = computed(() => {
  if (!result.value?.content) return ''
  return DOMPurify.sanitize(marked.parse(result.value.content))
})

async function loadProducts() {
  const res = await api.get('/products?status=')
  products.value = res.data
}

async function generate() {
  loading.value = true
  error.value = ''
  result.value = null
  try {
    const res = await api.post('/ai/script', { product_id: Number(productId.value), style: style.value, platform: platform.value })
    result.value = res.data.result
  } catch (e) {
    error.value = e.response?.data?.detail || e.message || '生成失败'
  } finally {
    loading.value = false
  }
}

async function exportFile(fmt) {
  if (!result.value) return
  const res = await api.post('/ai/script/export', {
    format: fmt,
    content: result.value.content,
    title: result.value.title || '脚本'
  }, { responseType: 'blob' })
  const url = URL.createObjectURL(new Blob([res.data]))
  const a = document.createElement('a')
  a.href = url
  a.download = `${result.value.title || '脚本'}.${fmt}`
  a.click()
}

function copy() {
  if (!result.value) return
  navigator.clipboard.writeText(result.value.content)
  alert('已复制')
}

onMounted(loadProducts)
</script>
