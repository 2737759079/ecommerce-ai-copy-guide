<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">AI文案生成</h2>
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
        <button @click="generate" :disabled="!productId || loading" class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-60">生成文案</button>
      </div>
      <p v-if="error" class="text-red-500 text-sm mt-3">{{ error }}</p>
    </div>
    <div v-if="result" class="bg-white rounded-xl shadow-sm p-6">
      <h3 class="font-bold text-lg mb-3">生成结果（可直接修改）</h3>
      <div class="space-y-3">
        <div>
          <label class="block text-sm text-gray-600 mb-1">标题</label>
          <input v-model="editableResult.title" class="w-full border rounded-lg px-3 py-2" />
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1">卖点</label>
          <textarea v-model="editableResult.selling_points" rows="3" class="w-full border rounded-lg px-3 py-2"></textarea>
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1">详情</label>
          <textarea v-model="editableResult.detail" rows="4" class="w-full border rounded-lg px-3 py-2"></textarea>
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1">广告语</label>
          <input v-model="editableResult.slogan" class="w-full border rounded-lg px-3 py-2" />
        </div>
      </div>
      <div class="mt-4 flex justify-end space-x-2">
        <button @click="copy" class="px-4 py-2 border rounded-lg hover:bg-gray-50">复制</button>
        <button @click="fillToProduct" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">一键填充到新增商品</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api/axios'

const router = useRouter()
const products = ref([])
const productId = ref('')
const style = ref('professional')
const result = ref(null)
const editableResult = ref({ title: '', selling_points: '', detail: '', slogan: '' })
const loading = ref(false)
const error = ref('')

const selectedProduct = computed(() => products.value.find(p => p.id === Number(productId.value)))

async function loadProducts() {
  const res = await api.get('/products?status=')
  products.value = res.data
}

async function generate() {
  loading.value = true
  error.value = ''
  result.value = null
  try {
    const res = await api.post('/ai/copy', { product_id: Number(productId.value), style: style.value })
    result.value = res.data.result
    editableResult.value = {
      title: res.data.result.title || '',
      selling_points: res.data.result.selling_points || '',
      detail: res.data.result.detail || '',
      slogan: res.data.result.slogan || '',
    }
  } catch (e) {
    error.value = e.response?.data?.detail || e.message || '生成失败'
  } finally {
    loading.value = false
  }
}

function copy() {
  if (!editableResult.value.title) return
  const text = `标题：${editableResult.value.title}\n卖点：${editableResult.value.selling_points}\n详情：${editableResult.value.detail}\n广告语：${editableResult.value.slogan}`
  navigator.clipboard.writeText(text)
  alert('已复制')
}

function fillToProduct() {
  if (!editableResult.value.title) {
    alert('请先生成文案')
    return
  }
  const desc = `${editableResult.value.detail}\n\n卖点：\n${editableResult.value.selling_points}\n\n广告语：${editableResult.value.slogan}`
  router.push({
    path: '/merchant/products',
    query: {
      autoOpenCreate: '1',
      name: editableResult.value.title,
      category: selectedProduct.value?.category || '',
      description: desc,
    }
  })
}

onMounted(loadProducts)
</script>
