<template>
  <div class="max-w-4xl mx-auto h-[calc(100vh-7rem)] fade-in-up">
    <div class="bg-white rounded-3xl shadow-card h-full flex flex-col overflow-hidden border border-primary-light/50">
      <!-- 头部 -->
      <div class="bg-gradient-to-r from-primary to-accent-blue px-6 py-4 flex items-center justify-between text-white shrink-0">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
            <ChatBubbleLeftRightIcon class="w-6 h-6" />
          </div>
          <div>
            <h2 class="font-bold text-lg">客服咨询</h2>
            <p class="text-xs text-white/80">商家在线回复中</p>
          </div>
        </div>
        <div v-if="product" class="hidden sm:flex items-center space-x-2 bg-white/20 backdrop-blur-sm rounded-xl px-3 py-1.5">
          <CubeIcon class="w-4 h-4" />
          <span class="text-sm">咨询商品：{{ product.name }}</span>
        </div>
      </div>

      <!-- 商品信息（移动端） -->
      <div v-if="product" class="sm:hidden px-4 py-2 bg-primary-light/30 border-b border-primary-light/50 text-sm text-primary-dark flex items-center space-x-2">
        <CubeIcon class="w-4 h-4" />
        <span>咨询商品：{{ product.name }}</span>
      </div>

      <!-- 消息区 -->
      <div ref="box" class="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 bg-page">
        <div v-if="messages.length === 0" class="text-center text-gray-400 py-10">
          <ChatBubbleLeftRightIcon class="w-12 h-12 mx-auto mb-3 text-primary/30" />
          <p>还没有消息，向商家提问吧～</p>
        </div>
        <div v-for="(msg, idx) in messages" :key="msg.id || idx" :class="msg.sender_role === 'user' ? 'text-right' : 'text-left'" class="fade-in-up">
          <div class="flex items-end space-x-2" :class="msg.sender_role === 'user' ? 'flex-row-reverse space-x-reverse' : ''">
            <img
              v-if="avatarFor(msg.sender_role)"
              :src="avatarFor(msg.sender_role)"
              class="w-9 h-9 rounded-full object-cover border-2 border-white shadow-sm flex-shrink-0"
            />
            <div
              v-else
              class="w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
              :class="msg.sender_role === 'user' ? 'bg-gradient-to-br from-primary to-accent-blue' : 'bg-gradient-to-br from-primary-dark to-primary'"
            >
              {{ msg.sender_role === 'user' ? '我' : '商' }}
            </div>
            <div
              class="inline-block px-4 py-2.5 rounded-2xl text-sm max-w-[78%] whitespace-pre-wrap leading-relaxed shadow-sm"
              :class="msg.sender_role === 'user'
                ? 'bg-gradient-to-r from-primary to-primary-dark text-white rounded-br-sm'
                : 'bg-white text-gray-800 border border-primary-light/50 rounded-bl-sm'"
            >
              {{ msg.content }}
            </div>
          </div>
          <p class="text-xs text-gray-400 mt-1" :class="msg.sender_role === 'user' ? 'pr-11' : 'pl-11'">{{ formatTime(msg.created_at) }}</p>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="p-4 bg-white border-t border-primary-light/50 shrink-0">
        <div class="flex items-center space-x-3">
          <FormInput v-model="input" @keydown.enter="send" type="text" placeholder="请输入您想咨询的问题" :icon="ChatBubbleBottomCenterTextIcon" class="flex-1" input-class="rounded-xl py-3" />
          <button
            @click="send"
            :disabled="!input.trim() || sending"
            class="bg-gradient-to-r from-primary to-primary-dark text-white px-5 py-3 rounded-xl hover:shadow-lg hover:shadow-primary/30 disabled:opacity-60 transition-all flex items-center space-x-1"
          >
            <PaperAirplaneIcon class="w-5 h-5" />
            <span class="hidden sm:inline">发送</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import api from '../../api/axios'
import FormInput from '../../components/ui/FormInput.vue'
import { ChatBubbleLeftRightIcon, CubeIcon, PaperAirplaneIcon, ChatBubbleBottomCenterTextIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const auth = useAuthStore()
const baseUrl = 'http://127.0.0.1:8000'

const messages = ref([])
const input = ref('')
const sending = ref(false)
const box = ref(null)
const product = ref(null)
let pollTimer = null

function avatarFor(role) {
  if (role === 'user') {
    const url = auth.user?.avatar_url
    return url ? (url.startsWith('http') ? url : baseUrl + url) : ''
  }
  return ''
}

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

async function loadMessages() {
  try {
    const res = await api.get('/cs/messages/my')
    messages.value = res.data
  } catch (e) {
    console.error('加载客服消息失败', e)
  }
}

async function loadProduct(id) {
  try {
    const res = await api.get(`/products/${id}`)
    product.value = res.data
  } catch (e) {
    product.value = null
  }
}

async function send() {
  const text = input.value.trim()
  if (!text || sending.value) return
  sending.value = true
  input.value = ''
  try {
    const payload = { content: text }
    if (product.value) payload.product_id = product.value.id
    await api.post('/cs/messages', payload)
    await loadMessages()
  } catch (e) {
    alert(e.response?.data?.detail || '发送失败')
  } finally {
    sending.value = false
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (box.value) box.value.scrollTop = box.value.scrollHeight
  })
}

watch(messages, scrollToBottom, { deep: true })

onMounted(() => {
  if (route.query.product_id) {
    loadProduct(route.query.product_id)
  }
  loadMessages()
  pollTimer = setInterval(loadMessages, 3000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>
