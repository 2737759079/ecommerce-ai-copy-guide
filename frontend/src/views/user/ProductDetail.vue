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
              :class="selectedImage === normalizeImage(img) ? 'border-primary ring-2 ring-primary-light' : 'border-transparent hover:border-gray-300'"
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
                :class="selectedSpec === spec ? 'bg-primary text-white border-primary shadow-md shadow-primary/20' : 'bg-gray-50 text-gray-700 border-gray-200 hover:border-primary/50 hover:text-primary'"
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

      <!-- 商品详情 -->
      <div class="mt-10 border-t pt-8">
        <div class="flex items-center space-x-2 mb-4">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent-blue flex items-center justify-center">
            <DocumentTextIcon class="w-4 h-4 text-white" />
          </div>
          <h3 class="text-lg font-bold text-gray-800">商品详情 / 精选推荐</h3>
        </div>
        <div class="bg-gradient-to-br from-primary-light to-accent-blue/20 rounded-2xl p-6 text-sm text-gray-700 space-y-4 border border-primary-light">
          <p><span class="font-semibold text-primary-dark">核心卖点：</span>{{ product.ai_selling_points || '暂无' }}</p>
          <p><span class="font-semibold text-primary-dark">商品介绍：</span>{{ product.ai_detail || '暂无' }}</p>
          <p><span class="font-semibold text-primary-dark">推荐语：</span>{{ product.ai_slogan || '暂无' }}</p>
        </div>
      </div>

      <!-- 用户评价 -->
      <div class="mt-10 border-t border-primary-light/50 pt-8">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-3">
          <div>
            <h3 class="text-lg font-bold text-gray-800 flex items-center space-x-2">
              <StarIcon class="w-5 h-5 text-yellow-400" />
              <span>用户评价</span>
            </h3>
            <p class="text-sm text-gray-500 mt-1 flex items-center space-x-2">
              <span class="font-bold text-gray-700">{{ averageRating }}</span>
              <span>分 / 共 {{ reviewCounts[''] }} 条评价</span>
            </p>
          </div>
          <div class="flex bg-white rounded-xl p-1 shadow-sm border border-primary-light/50">
            <button
              v-for="tab in reviewTabs"
              :key="tab.value"
              @click="reviewSentiment = tab.value"
              :class="reviewSentiment === tab.value ? 'bg-primary-light text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'"
              class="px-4 py-1.5 rounded-lg text-sm font-medium transition-all"
            >{{ tab.label }} ({{ reviewCounts[tab.value] }})</button>
          </div>
        </div>
        <div v-if="filteredReviews.length === 0" class="text-gray-500 text-sm bg-white rounded-2xl p-8 text-center shadow-card border border-primary-light/30">暂无评价</div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div v-for="(r, idx) in filteredReviews" :key="r.id" class="card card-hover rounded-2xl p-5 fade-in-up" :style="{ animationDelay: idx * 50 + 'ms' }">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center space-x-2">
                <div class="w-9 h-9 rounded-full bg-gradient-to-br from-primary to-accent-blue flex items-center justify-center text-white text-xs font-bold">
                  {{ (r.user_nickname || 'U').charAt(0).toUpperCase() }}
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-700 block">{{ r.user_nickname || '匿名用户' }}</span>
                  <span class="text-xs text-gray-400">{{ new Date(r.created_at).toLocaleDateString() }}</span>
                </div>
              </div>
              <span :class="sentimentClass(r.sentiment)" class="badge">{{ sentimentText(r.sentiment) }}</span>
            </div>
            <div class="flex items-center mb-3">
              <span class="text-yellow-400 text-sm">{{ '★'.repeat(r.rating) }}{{ '☆'.repeat(5 - r.rating) }}</span>
            </div>
            <p class="text-sm text-gray-700 leading-relaxed mb-3">{{ r.content }}</p>
            <div v-if="r.images && r.images.length" class="flex flex-wrap gap-2 mb-3">
              <img
                v-for="(img, idx) in r.images"
                :key="idx"
                :src="normalizeImage(img)"
                class="w-16 h-16 object-cover rounded-lg border cursor-pointer hover:opacity-90"
                @click="previewImage = normalizeImage(img)"
              />
            </div>
            <video v-if="r.video_url" :src="normalizeImage(r.video_url)" controls class="h-32 rounded-lg"></video>
          </div>
        </div>
      </div>

      <div v-if="previewImage" @click="previewImage = ''" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
        <img :src="previewImage" class="max-w-full max-h-full rounded-lg" />
      </div>
    </div>
  </div>
  <div v-else class="text-center py-24 fade-in-up">
    <div class="inline-block animate-spin rounded-full h-10 w-10 border-4 border-primary-light border-t-primary mb-4"></div>
    <p class="text-gray-500">加载中...</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../api/axios'
import {
  PhotoIcon,
  CubeIcon,
  TagIcon,
  ShoppingCartIcon,
  HeartIcon,
  DocumentTextIcon,
  StarIcon,
} from '@heroicons/vue/24/outline'

const route = useRoute()
const product = ref(null)
const allReviews = ref([])
const reviewsLoaded = ref(false)
const selectedSpec = ref('')
const favorited = ref(false)
const selectedImage = ref('')
const previewImage = ref('')
const reviewSentiment = ref('')
const reviewTabs = [
  { label: '全部', value: '' },
  { label: '好评', value: 'positive' },
  { label: '中评', value: 'neutral' },
  { label: '差评', value: 'negative' },
]
const baseUrl = 'http://127.0.0.1:8000'

const filteredReviews = computed(() => {
  if (!reviewSentiment.value) return allReviews.value
  return allReviews.value.filter(r => r.sentiment === reviewSentiment.value)
})

const reviewCounts = computed(() => ({
  '': allReviews.value.length,
  positive: allReviews.value.filter(r => r.sentiment === 'positive').length,
  neutral: allReviews.value.filter(r => r.sentiment === 'neutral').length,
  negative: allReviews.value.filter(r => r.sentiment === 'negative').length,
}))

const averageRating = computed(() => {
  if (!allReviews.value.length) return '0.0'
  const avg = allReviews.value.reduce((sum, r) => sum + (r.rating || 0), 0) / allReviews.value.length
  return avg.toFixed(1)
})

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
  if (reviewsLoaded.value) return
  const res = await api.get(`/reviews/product/${route.params.id}`)
  allReviews.value = res.data
  reviewsLoaded.value = true
}

watch(reviewSentiment, loadReviews)

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
