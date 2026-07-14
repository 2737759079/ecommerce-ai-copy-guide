<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">直播/短视频脚本生成</h2>
    <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
      <div class="flex flex-col md:flex-row gap-4 items-end">
        <FormSelect v-model="productId" label="选择商品" :icon="CubeIcon" placeholder="请选择商品" class="flex-1">
          <option value="">请选择商品</option>
          <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
        </FormSelect>
        <FormSelect v-model="style" label="脚本风格" :icon="SwatchIcon" placeholder="请选择风格">
          <option value="professional">专业</option>
          <option value="concise">简洁</option>
          <option value="premium">高端</option>
          <option value="lively">活泼</option>
          <option value="promotional">促销</option>
          <option value="lifestyle">生活化</option>
        </FormSelect>
        <FormSelect v-model="platform" label="生成平台" :icon="VideoCameraIcon" placeholder="请选择平台">
          <option value="live">直播脚本</option>
          <option value="short">短视频脚本</option>
        </FormSelect>
        <button
          @click="generate"
          :disabled="!productId || loading"
          class="bg-primary text-white px-6 py-2 rounded-lg hover:bg-primary-dark disabled:opacity-60 flex items-center justify-center space-x-2"
        >
          <svg v-if="loading" class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span>{{ loading ? '生成中...' : '生成脚本' }}</span>
        </button>
      </div>
      <p v-if="error" class="text-red-500 text-sm mt-3">{{ error }}</p>
    </div>

    <div v-if="result" class="bg-white rounded-xl shadow-sm p-6">
      <div class="flex justify-between items-center mb-3 flex-wrap gap-3">
        <h3 class="font-bold text-lg">生成结果</h3>
        <div class="flex items-center space-x-2">
          <button
            @click="isEditing = !isEditing"
            class="px-3 py-1.5 border rounded-lg text-sm hover:bg-gray-50"
          >{{ isEditing ? '预览' : '编辑' }}</button>
          <button @click="exportFile('txt')" class="px-3 py-1.5 border rounded-lg text-sm hover:bg-gray-50">导出TXT</button>
          <button @click="exportFile('docx')" class="px-3 py-1.5 border rounded-lg text-sm hover:bg-gray-50">导出Word</button>
          <button @click="copy" class="px-3 py-1.5 border rounded-lg text-sm hover:bg-gray-50">复制</button>
        </div>
      </div>
      <FormInput
        v-if="isEditing"
        v-model="editableContent"
        label="生成脚本"
        :icon="DocumentTextIcon"
        type="textarea"
        :rows="16"
        placeholder="生成的脚本内容将显示在这里"
        input-class="font-mono text-sm"
      />
      <div v-else class="prose max-w-none bg-gray-50 p-4 rounded-lg text-sm text-gray-700" v-html="renderedMarkdown"></div>
    </div>

    <AppLoading v-if="loading" message="AI 正在生成脚本，请稍候..." />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import api from '../../api/axios'
import FormInput from '../../components/ui/FormInput.vue'
import FormSelect from '../../components/ui/FormSelect.vue'
import AppLoading from '../../components/AppLoading.vue'
import { CubeIcon, SwatchIcon, VideoCameraIcon, DocumentTextIcon } from '@heroicons/vue/24/outline'

const products = ref([])
const productId = ref('')
const style = ref('professional')
const platform = ref('live')
const result = ref(null)
const editableContent = ref('')
const isEditing = ref(true)
const loading = ref(false)
const error = ref('')

const renderedMarkdown = computed(() => {
  if (!editableContent.value) return ''
  return DOMPurify.sanitize(marked.parse(editableContent.value))
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
    editableContent.value = res.data.result.content || ''
    isEditing.value = true
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
    content: editableContent.value,
    title: result.value.title || '脚本'
  }, { responseType: 'blob' })
  const url = URL.createObjectURL(new Blob([res.data]))
  const a = document.createElement('a')
  a.href = url
  a.download = `${result.value.title || '脚本'}.${fmt}`
  a.click()
}

function copy() {
  if (!editableContent.value) return
  navigator.clipboard.writeText(editableContent.value)
  alert('已复制')
}

onMounted(loadProducts)
</script>
