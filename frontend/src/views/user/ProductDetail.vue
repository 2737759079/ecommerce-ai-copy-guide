<template>
  <div v-if="product" class="fade-in-up">
    <div class="bg-white rounded-3xl shadow-lg p-6 md:p-8">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <!-- 图片区 -->
        <div class="space-y-4">
          <div class="h-80 md:h-96 bg-gray-100 rounded-2xl flex items-center justify-center overflow-hidden group relative">
            <img v-if="selectedImage" :src="selectedImage" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
            <div v-else class="flex flex-col items-center text-gray-400">
              <PhotoIcon class="w-16 h-16 mb-2" />
              <span>暂无图片</span>
            </div>
            <div class="absolute top-4 left-4">
              <span class="badge badge-indigo">{{ product.category }}</span>
            </div>
          </div>
          <div v-if="product.images && product.images.length > 1" class="flex gap-3 overflow-x-auto pb-2">
            <button
              v-for="(img, idx) in product.images"
              :key="idx"
              @click="selectedImage = normalizeImage(img)"
              class="w-16 h-16 rounded-xl overflow-hidden border-2 flex-shrink-0 transition-all"
              :class="selectedImage === normalizeImage(img) ? 'border-indigo-600 ring-2 ring-indigo-100' : 'border-transparent hover:border-gray-300'"
            >
              <img :src="normalizeImage(img)" class="w-full h-full object-cover" />
            </button>
          </div>
        </div>

        <!-- 信息区 -->
        <div class="flex flex-col">
          <h1 class="text-2xl md:text-3xl font-bold text-gray-800 leading-snug">{{ product.ai_title || product.name }}</h1>
          <div class="mt-4 flex items-baseline space-x-2">
            <span class="text-sm text-gray-500">售价</span>
            <span class="text-3xl font-bold text-gradient">¥{{ product.price }}</span>
          </div>
          <div class="mt-4 flex items-center space-x-4 text-sm text-gray-500">
            <span class="flex items-center space-x-1"><CubeIcon class="w-4 h-4" /><span>库存：{{ product.stock }}</span></span>
            <span class="flex items-center space-x-1"><TagIcon class="w-4 h-4" /><span>商品ID：{{ product.display_id }}</span></span>
          </div>

          <div class="mt-6" v-if="product.specs && product.specs.length">
            <label class="block text-sm font-medium text-gray-700 mb-2">选择规格</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="spec in product.specs"
                :key="spec"
                @click="selectedSpec = spec"
                :class="selectedSpec === spec ? 'bg-indigo-600 text-white border-indigo-600 shadow-md shadow-indigo-200' : 'bg-gray-50 text-gray-700 border-gray-200 hover:border-indigo-300 hover:text-indigo-600'"
                class="px-4 py-2 rounded-xl text-sm border transition-all"
              >
                {{ spec }}
              </button>
            </div>
          </div>

          <div class="mt-auto pt-8 flex space-x-4">
            <button @click="addToCart" class="flex-1 btn-primary py-3 flex items-center justify-center space-x-2 text-base">
              <ShoppingCartIcon class="w-5 h-5" />
              <span>加入购物车</span>
            </button>
            <button @click="toggleFavorite" :class="favorited ? 'bg-red-50 border-red-200 text-red-500' : 'bg-white border-gray-200 text-gray-600 hover:border-red-200 hover:text-red-500'" class="px-5 py-3 rounded-xl border transition-all flex items-center space-x-2">
              <HeartIcon :class="favorited ? 'fill-current' : ''" class="w-5 h-5" />
              <span>{{ favorited ? '已收藏' : '收藏' }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- AI 生成详情 -->
      <div class="mt-10 border-t pt-8">
        <div class="flex items-center space-x-2 mb-4">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-pink-500 flex items-center justify-center">
            <SparklesIcon class="w-4 h-4 text-white" />
          </div>
          <h3 class="text-lg font-bold text-gray-800">AI 生成详情</h3>
        </div>
        <div class="bg-gradient-to-br from-indigo-50 to-violet-50 rounded-2xl p-6 text-sm text-gray-700 space-y-4 border border-indigo-100">
          <p><span class="font-semibold text-indigo-700">核心卖点：</span>{{ product.ai_selling_points || '暂无' }}</p>
          <p><span class="font-semibold text-indigo-700">详情文案：</span>{{ product.ai_detail || '暂无' }}</p>
          <p><span class="font-semibold text-indigo-700">广告语：</span>{{ product.ai_slogan || '暂无' }}</p>
        </div>
      </div>

      <!-- 用户评价 -->
      <div class="mt-10 border-t pt-8">
        <h3 class="text-lg font-bold text-gray-800 mb-4">用户评价</h3>
        <div v-if="reviews.length === 0" class="text-gray-500 text-sm bg-gray-50 rounded-xl p-6 text-center">暂无评价</div>
        <div v-else class="space-y-3">
          <div v-for="r in reviews" :key="r.id" class="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm hover:shadow-md transition-shadow">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center space-x-2">
                <div class="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-400 to-pink-400 flex items-center justify-center text-white text-xs font-bold">
                  {{ (r.user_nickname || 'U').charAt(0).toUpperCase() }}
                </div>
                <span class="text-sm font-medium text-gray-700">{{ r.user_nickname || '匿名用户' }}</span>
              </div>
              <span :class="sentimentClass(r.sentiment)" class="badge">{{ sentimentText(r.sentiment) }}</span>
            </div>
            <div class="flex items-center mb-2">
              <span class="text-yellow-400 text-sm">{{ '★'.repeat(r.rating) }}{{ '☆'.repeat(5 - r.rating) }}</span>
              <span class="text-xs text-gray-400 ml-2">{{ new Date(r.created_at).toLocaleDateString() }}</span>
            </div>
            <p class="text-sm text-gray-700">{{ r.content }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="text-center py-24 fade-in-up">
    <div class="inline-block animate-spin rounded-full h-10 w-10 border-4 border-indigo-200 border-t-indigo-600 mb-4"></div>
    <p class="text-gray-500">加载中...</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../api/axios'
import {
  PhotoIcon,
  CubeIcon,
  TagIcon,
  ShoppingCartIcon,
  HeartIcon,
  SparklesIcon,
} from '@heroicons/vue/24/outline'

const route = useRoute()
const product = ref(null)
const reviews = ref([])
const selectedSpec = ref('')
const favorited = ref(false)
const selectedImage = ref('')
const baseUrl = 'http://127.0.0.1:8000'

function normalizeImage(url) {
  if (!url) return ''
  return url.startsWith('http') ? url : baseUrl + url
}

async function loadProduct() {
  const res = await api.get(`/products/${route.params.id}`)
  product.value = res.data
  if (res.data.specs && res.data.specs.length) selectedSpec.value = res.data.specs[0]
  const images = res.data.images || []
  selectedImage.value = images.length ? normalizeImage(images[0]) : normalizeImage(res.data.image_url)
  await api.post(`/products/${route.params.id}/browse`)
}

async function loadReviews() {
  const res = await api.get(`/reviews/product/${route.params.id}`)
  reviews.value = res.data
}

function addToCart() {
  const cart = JSON.parse(localStorage.getItem('cart') || '[]')
  const item = {
    product_id: product.value.id,
    name: product.value.name,
    price: product.value.price,
    spec: selectedSpec.value,
    quantity: 1,
    image_url: selectedImage.value,
    images: product.value.images,
  }
  const exist = cart.find(i => i.product_id === item.product_id && i.spec === item.spec)
  if (exist) {
    exist.quantity += 1
  } else {
    cart.push(item)
  }
  localStorage.setItem('cart', JSON.stringify(cart))
  alert('已加入购物车')
}

async function toggleFavorite() {
  const res = await api.post(`/products/${route.params.id}/favorite`)
  favorited.value = res.data.favorited
}

function sentimentText(s) {
  const map = { positive: '好评', neutral: '中评', negative: '差评' }
  return map[s] || s
}

function sentimentClass(s) {
  return s === 'positive' ? 'badge-green' : s === 'negative' ? 'badge-red' : 'badge-yellow'
}

onMounted(async () => {
  await loadProduct()
  await loadReviews()
})
</script>
