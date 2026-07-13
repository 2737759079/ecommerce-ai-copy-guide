<template>
  <div class="fade-in-up">
    <!-- 搜索区 -->
    <div class="bg-white/80 backdrop-blur-md rounded-2xl shadow-lg p-5 mb-8 border border-white/50">
      <div class="flex flex-col md:flex-row gap-4">
        <div class="relative flex-1">
          <MagnifyingGlassIcon class="w-5 h-5 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input v-model="keyword" @keydown.enter="loadProducts" type="text" placeholder="搜索心仪商品" class="input-modern pl-11 w-full" />
        </div>
        <div class="relative md:w-56">
          <FunnelIcon class="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <select v-model="category" @change="loadProducts" class="input-modern pl-10 w-full appearance-none cursor-pointer">
            <option value="">全部分类</option>
            <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
        <button @click="loadProducts" class="btn-primary flex items-center justify-center space-x-2 px-8">
          <MagnifyingGlassIcon class="w-4 h-4" />
          <span>搜索</span>
        </button>
      </div>
      <div class="mt-4 flex flex-wrap gap-2">
        <span class="text-xs text-gray-500 py-1.5">热门分类：</span>
        <button
          v-for="c in categories.slice(0, 6)"
          :key="c"
          @click="category = c; loadProducts()"
          :class="category === c ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-indigo-50 hover:text-indigo-600'"
          class="text-xs px-3 py-1.5 rounded-full transition-colors"
        >
          {{ c }}
        </button>
      </div>
    </div>

    <!-- 加载/空态/商品列表 -->
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <div v-for="n in 8" :key="n" class="bg-white rounded-2xl shadow-md p-4 h-72 animate-pulse">
        <div class="bg-gray-200 rounded-xl h-40 mb-4"></div>
        <div class="bg-gray-200 rounded h-4 w-3/4 mb-3"></div>
        <div class="bg-gray-200 rounded h-3 w-1/2"></div>
      </div>
    </div>
    <div v-else-if="products.length === 0" class="text-center py-24 fade-in-up">
      <div class="w-20 h-20 bg-indigo-50 rounded-full flex items-center justify-center mx-auto mb-4">
        <MagnifyingGlassIcon class="w-10 h-10 text-indigo-400" />
      </div>
      <p class="text-gray-500 text-lg">暂无商品</p>
      <p class="text-sm text-gray-400 mt-1">换个关键词试试吧</p>
    </div>
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <ProductCard v-for="(p, idx) in products" :key="p.id" :product="p" @click="goDetail(p.id)" class="fade-in-up" :style="{ animationDelay: idx * 50 + 'ms' }" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api/axios'
import ProductCard from '../../components/ProductCard.vue'
import { MagnifyingGlassIcon, FunnelIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const products = ref([])
const categories = ref([])
const keyword = ref('')
const category = ref('')
const loading = ref(false)

async function loadProducts() {
  loading.value = true
  try {
    const params = { status: 'on' }
    if (keyword.value) params.keyword = keyword.value
    if (category.value) params.category = category.value
    const res = await api.get('/products', { params })
    products.value = res.data
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  try {
    const res = await api.get('/products/categories/list')
    categories.value = res.data
  } catch (e) {}
}

function goDetail(id) {
  router.push(`/product/${id}`)
}

onMounted(() => {
  loadCategories()
  loadProducts()
})
</script>
