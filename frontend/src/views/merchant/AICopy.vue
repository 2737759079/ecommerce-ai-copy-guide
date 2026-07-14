<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">AI文案生成</h2>

    <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
      <div class="flex justify-center mb-6">
        <div class="inline-flex p-1 bg-gray-100 rounded-xl">
          <button
            @click="mode = 'existing'"
            :class="mode === 'existing' ? 'bg-white shadow-md text-primary' : 'text-gray-500 hover:text-gray-700'"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
          >选择已有商品</button>
          <button
            @click="mode = 'manual'"
            :class="mode === 'manual' ? 'bg-white shadow-md text-primary' : 'text-gray-500 hover:text-gray-700'"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
          >手动输入新商品</button>
        </div>
      </div>

      <div class="flex flex-col md:flex-row gap-4 mb-4 items-end">
        <template v-if="mode === 'existing'">
          <FormSelect v-model="productId" label="选择商品" :icon="CubeIcon" placeholder="请选择商品" class="flex-1">
            <option value="">请选择商品</option>
            <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
          </FormSelect>
        </template>
        <template v-else>
          <FormInput v-model="manualProduct.name" label="商品名称" :icon="CubeIcon" placeholder="请输入商品名称" class="flex-1" />
        </template>
        <FormSelect v-model="style" label="文案风格" :icon="SwatchIcon" placeholder="请选择风格">
          <option value="professional">专业</option>
          <option value="concise">简洁</option>
          <option value="premium">高端</option>
          <option value="lively">活泼</option>
          <option value="promotional">促销</option>
          <option value="lifestyle">生活化</option>
        </FormSelect>
        <button
          @click="generate"
          :disabled="!canGenerate || loading"
          class="bg-primary text-white px-6 py-2 rounded-lg hover:bg-primary-dark disabled:opacity-60 flex items-center justify-center space-x-2"
        >
          <svg v-if="loading" class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span>{{ loading ? '生成中...' : '生成文案' }}</span>
        </button>
      </div>

      <div v-if="mode === 'manual'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormInput v-model="manualProduct.category" label="商品分类" :icon="TagIcon" placeholder="请输入商品分类" />
        <FormInput v-model="manualProduct.price" label="商品价格" :icon="CurrencyYenIcon" type="number" step="0.01" placeholder="请输入商品价格" />
        <FormInput v-model="manualProduct.specs" label="商品规格" :icon="ListBulletIcon" placeholder="请输入商品规格，用逗号分隔" input-class="md:col-span-2" />
        <FormInput v-model="manualProduct.description" label="商品描述" :icon="DocumentTextIcon" type="textarea" :rows="3" placeholder="请输入商品描述" input-class="md:col-span-2" />
      </div>

      <p v-if="error" class="text-red-500 text-sm mt-3">{{ error }}</p>
    </div>

    <div v-if="result" class="bg-white rounded-xl shadow-sm p-6">
      <h3 class="font-bold text-lg mb-3">生成结果（可直接修改）</h3>
      <div class="space-y-3">
        <FormInput v-model="editableResult.title" label="标题" :icon="ChatBubbleBottomCenterTextIcon" placeholder="请输入标题" />
        <FormInput v-model="editableResult.selling_points" label="卖点" :icon="StarIcon" type="textarea" :rows="3" placeholder="请输入卖点" />
        <FormInput v-model="editableResult.detail" label="详情" :icon="DocumentTextIcon" type="textarea" :rows="4" placeholder="请输入详情" />
        <FormInput v-model="editableResult.slogan" label="广告语" :icon="MegaphoneIcon" placeholder="请输入广告语" />
      </div>
      <div class="mt-4 flex justify-end space-x-2">
        <button @click="copy" class="px-4 py-2 border rounded-lg hover:bg-gray-50">复制</button>
        <button @click="fillToProduct" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">一键填充到新增商品</button>
      </div>
    </div>

    <AppLoading v-if="loading" message="AI 正在生成文案，请稍候..." />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api/axios'
import FormInput from '../../components/ui/FormInput.vue'
import FormSelect from '../../components/ui/FormSelect.vue'
import AppLoading from '../../components/AppLoading.vue'
import {
  CubeIcon,
  SwatchIcon,
  TagIcon,
  CurrencyYenIcon,
  ListBulletIcon,
  DocumentTextIcon,
  ChatBubbleBottomCenterTextIcon,
  StarIcon,
  MegaphoneIcon,
} from '@heroicons/vue/24/outline'

const router = useRouter()
const products = ref([])
const productId = ref('')
const style = ref('professional')
const mode = ref('existing')
const manualProduct = ref({ name: '', category: '', description: '', price: '', specs: '' })
const result = ref(null)
const editableResult = ref({ title: '', selling_points: '', detail: '', slogan: '' })
const loading = ref(false)
const error = ref('')

const selectedProduct = computed(() => products.value.find(p => p.id === Number(productId.value)))

const canGenerate = computed(() => {
  if (mode.value === 'existing') return !!productId.value
  return !!manualProduct.value.name.trim()
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
    const payload = { style: style.value }
    if (mode.value === 'existing') {
      payload.product_id = Number(productId.value)
    } else {
      payload.name = manualProduct.value.name
      payload.category = manualProduct.value.category
      payload.description = manualProduct.value.description
      payload.price = parseFloat(manualProduct.value.price || 0)
      payload.specs = manualProduct.value.specs.split(',').map(s => s.trim()).filter(Boolean)
    }
    const res = await api.post('/ai/copy', payload)
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
      category: mode.value === 'existing' ? (selectedProduct.value?.category || '') : manualProduct.value.category,
      description: desc,
    }
  })
}

onMounted(loadProducts)
</script>
