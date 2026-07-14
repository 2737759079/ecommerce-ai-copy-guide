<template>
  <img
    v-if="src"
    :src="normalizedSrc"
    :alt="alt"
    class="object-cover"
    :class="[sizeClass, imgClass]"
    @error="$emit('error')"
  />
  <div v-else :class="['flex items-center justify-center bg-gray-100 text-gray-400', sizeClass, imgClass]">
    <PhotoIcon class="w-1/3 h-1/3" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { PhotoIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  src: { type: String, default: '' },
  alt: { type: String, default: '' },
  size: { type: String, default: 'md' },
  imgClass: { type: String, default: '' },
})
const emit = defineEmits(['error'])

const baseUrl = 'http://127.0.0.1:8000'

const normalizedSrc = computed(() => {
  if (!props.src) return ''
  return props.src.startsWith('http') ? props.src : baseUrl + props.src
})

const sizeClass = computed(() => {
  const map = {
    sm: 'w-10 h-10 rounded-lg',
    md: 'w-16 h-16 rounded-xl',
    lg: 'w-24 h-24 rounded-2xl',
    full: 'w-full h-full',
  }
  return map[props.size] || map.md
})
</script>
