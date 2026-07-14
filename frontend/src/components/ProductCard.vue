<template>
  <div class="group bg-white rounded-2xl shadow-md hover:shadow-xl hover:-translate-y-1.5 transition-all duration-300 overflow-hidden cursor-pointer border border-gray-100" @click="$emit('click')">
    <div class="h-44 bg-gray-100 flex items-center justify-center overflow-hidden relative">
      <img v-if="firstImage" :src="firstImage" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
      <div v-else class="flex flex-col items-center text-gray-400">
        <PhotoIcon class="w-10 h-10 mb-1" />
        <span class="text-xs">暂无图片</span>
      </div>
      <div class="absolute top-3 right-3">
        <span class="badge badge-indigo">{{ product.category }}</span>
      </div>
    </div>
    <div class="p-4">
      <h3 class="font-semibold text-gray-800 truncate group-hover:text-primary transition-colors">{{ product.ai_title || product.name }}</h3>
      <p class="text-xs text-gray-500 mt-1.5 line-clamp-2 h-8">{{ product.ai_slogan || product.description || '暂无描述' }}</p>
      <div class="mt-3 flex items-center justify-between">
        <span class="text-lg font-bold text-gradient">¥{{ product.price }}</span>
        <span class="text-xs text-gray-400 flex items-center space-x-1">
          <ShoppingCartIcon class="w-3.5 h-3.5" />
          <span>抢购</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { PhotoIcon, ShoppingCartIcon } from '@heroicons/vue/24/outline'

const props = defineProps({ product: Object })
defineEmits(['click'])

const baseUrl = 'http://127.0.0.1:8000'
const firstImage = computed(() => {
  const images = props.product.images || []
  const url = images[0] || props.product.image_url || ''
  if (!url) return ''
  return url.startsWith('http') ? url : baseUrl + url
})
</script>
