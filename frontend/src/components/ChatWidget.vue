<template>
  <div class="fixed bottom-6 right-6 z-50 flex flex-col items-end">
    <div v-if="open" class="bg-white w-80 sm:w-96 h-[520px] rounded-2xl shadow-2xl flex flex-col border border-primary-light/50 mb-4 overflow-hidden modal-in">
      <div class="bg-gradient-to-r from-primary to-accent-blue text-white px-5 py-4 flex justify-between items-center">
        <div class="flex items-center space-x-2">
          <SparklesIcon class="w-5 h-5" />
          <span class="font-medium">AI智能导购</span>
        </div>
        <button @click="open = false" class="text-white/80 hover:text-white hover:bg-white/20 rounded-lg p-1 transition-colors">
          <XMarkIcon class="w-5 h-5" />
        </button>
      </div>
      <div ref="box" class="flex-1 overflow-y-auto p-4 space-y-4 bg-page">
        <div v-for="(msg, idx) in messages" :key="idx" :class="msg.role === 'user' ? 'text-right' : 'text-left'" class="fade-in-up" :style="{ animationDelay: idx * 50 + 'ms' }">
          <div class="flex items-end space-x-2" :class="msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''">
            <div class="w-7 h-7 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold" :class="msg.role === 'user' ? 'bg-gradient-to-br from-primary to-accent-blue text-white' : 'bg-gradient-to-br from-primary to-primary-dark text-white'">
              {{ msg.role === 'user' ? '我' : 'AI' }}
            </div>
            <div :class="msg.role === 'user' ? 'bg-gradient-to-r from-primary to-primary-dark text-white rounded-br-sm' : 'bg-white text-gray-800 border border-primary-light/50 shadow-sm rounded-bl-sm'" class="inline-block px-4 py-2.5 rounded-2xl text-sm max-w-[78%] whitespace-pre-wrap leading-relaxed">
              {{ msg.content }}
            </div>
          </div>
        </div>
        <div v-if="loading" class="text-left fade-in-up">
          <div class="flex items-center space-x-2">
            <div class="w-7 h-7 rounded-full bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center text-xs font-bold text-white">AI</div>
            <div class="bg-white text-gray-500 border border-primary-light/50 shadow-sm inline-flex items-center space-x-1 px-4 py-2.5 rounded-2xl text-sm">
              <span class="w-1.5 h-1.5 bg-primary rounded-full animate-bounce"></span>
              <span class="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style="animation-delay: 0.1s"></span>
              <span class="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
            </div>
          </div>
        </div>
      </div>
      <div class="p-4 border-t border-primary-light/50 bg-white">
        <div class="flex space-x-2">
          <FormInput v-model="input" @keydown.enter="send" type="text" placeholder="咨询尺码、材质、售后等" :icon="ChatBubbleLeftRightIcon" class="flex-1" input-class="rounded-xl py-2.5" />
          <button @click="send" :disabled="loading || !input.trim()" class="bg-gradient-to-r from-primary to-primary-dark text-white px-4 py-2.5 rounded-xl hover:shadow-lg hover:shadow-primary/30 disabled:opacity-60 transition-all">
            <PaperAirplaneIcon class="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
    <button @click="open = !open" class="relative w-14 h-14 rounded-full bg-gradient-to-r from-primary via-primary-light to-accent-blue text-white shadow-lg shadow-primary/40 hover:shadow-xl hover:shadow-primary/50 hover:scale-105 transition-all duration-300 flex items-center justify-center pulse-ring">
      <ChatBubbleLeftEllipsisIcon v-if="!open" class="w-7 h-7" />
      <XMarkIcon v-else class="w-7 h-7" />
    </button>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'
import FormInput from './ui/FormInput.vue'
import {
  SparklesIcon,
  XMarkIcon,
  PaperAirplaneIcon,
  ChatBubbleLeftEllipsisIcon,
  ChatBubbleLeftRightIcon,
} from '@heroicons/vue/24/solid'

const open = ref(false)
const input = ref('')
const loading = ref(false)
const messages = ref([{ role: 'assistant', content: '您好！我是AI智能导购，请问有什么可以帮您？' }])
const box = ref(null)
const route = useRoute()

const productId = ref(null)

onMounted(() => {
  if (route.params.id) {
    productId.value = parseInt(route.params.id)
  }
})

watch(() => route.params.id, (val) => {
  productId.value = val ? parseInt(val) : null
})

watch(messages, () => {
  nextTick(() => {
    if (box.value) box.value.scrollTop = box.value.scrollHeight
  })
}, { deep: true })

async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return
  messages.value.push({ role: 'user', content: text })
  input.value = ''
  loading.value = true
  try {
    const payload = { message: text }
    if (productId.value) payload.product_id = productId.value
    const res = await api.post('/chat/ask', payload)
    messages.value.push({ role: 'assistant', content: res.data.answer })
  } catch (e) {
    messages.value.push({ role: 'assistant', content: '抱歉，服务暂时不可用，请稍后再试。' })
  } finally {
    loading.value = false
  }
}
</script>
