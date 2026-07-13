<template>
  <div class="max-w-5xl mx-auto fade-in-up">
    <div class="bg-white rounded-3xl shadow-lg p-6 md:p-8">
      <div class="flex items-center space-x-2 mb-6">
        <ShoppingCartIcon class="w-6 h-6 text-indigo-600" />
        <h2 class="text-2xl font-bold text-gray-800">购物车</h2>
      </div>

      <div v-if="cart.length === 0" class="text-center py-24">
        <div class="w-24 h-24 bg-indigo-50 rounded-full flex items-center justify-center mx-auto mb-4">
          <ShoppingCartIcon class="w-12 h-12 text-indigo-300" />
        </div>
        <p class="text-gray-500 text-lg">购物车是空的</p>
        <router-link to="/home" class="inline-block mt-4 btn-primary px-6">去逛逛</router-link>
      </div>

      <div v-else class="space-y-6">
        <div v-for="(item, idx) in cart" :key="idx" class="flex flex-col sm:flex-row sm:items-center justify-between bg-gray-50 rounded-2xl p-4 border border-gray-100 hover:shadow-md transition-shadow">
          <div class="flex items-center space-x-4">
            <div class="w-20 h-20 bg-white rounded-xl flex items-center justify-center overflow-hidden shadow-sm flex-shrink-0">
              <img v-if="firstImage(item)" :src="firstImage(item)" class="w-full h-full object-cover" />
              <PhotoIcon v-else class="w-8 h-8 text-gray-300" />
            </div>
            <div>
              <h3 class="font-semibold text-gray-800">{{ item.name }}</h3>
              <p class="text-sm text-gray-500 mt-1">规格：{{ item.spec || '默认' }}</p>
              <p class="text-lg font-bold text-gradient mt-1">¥{{ item.price }}</p>
            </div>
          </div>
          <div class="flex items-center space-x-4 mt-4 sm:mt-0">
            <div class="flex items-center bg-white rounded-xl border border-gray-200 shadow-sm">
              <button @click="changeQty(idx, -1)" class="px-3 py-2 hover:bg-gray-50 rounded-l-xl transition-colors">
                <MinusIcon class="w-4 h-4 text-gray-600" />
              </button>
              <span class="px-4 font-medium text-gray-800 min-w-[3rem] text-center">{{ item.quantity }}</span>
              <button @click="changeQty(idx, 1)" class="px-3 py-2 hover:bg-gray-50 rounded-r-xl transition-colors">
                <PlusIcon class="w-4 h-4 text-gray-600" />
              </button>
            </div>
            <button @click="remove(idx)" class="flex items-center space-x-1 text-red-500 hover:text-red-600 hover:bg-red-50 px-3 py-2 rounded-xl transition-all">
              <TrashIcon class="w-4 h-4" />
              <span class="text-sm">删除</span>
            </button>
          </div>
        </div>

        <div class="bg-gradient-to-br from-indigo-50 to-violet-50 rounded-2xl p-6 border border-indigo-100">
          <p class="text-sm font-medium text-gray-700 mb-3 flex items-center space-x-2">
            <MapPinIcon class="w-4 h-4 text-indigo-600" />
            <span>收货地址（必填）</span>
          </p>
          <div v-if="addresses.length" class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
            <div
              v-for="addr in addresses"
              :key="addr.id"
              @click="selectAddress(addr)"
              :class="selectedAddress?.id === addr.id ? 'border-indigo-500 bg-white shadow-md' : 'border-gray-200 bg-white hover:border-indigo-300'"
              class="border rounded-xl p-3 cursor-pointer transition-all relative"
            >
              <div class="flex items-start space-x-2">
                <CheckCircleIcon v-if="selectedAddress?.id === addr.id" class="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" />
                <div v-else class="w-5 h-5 rounded-full border-2 border-gray-300 flex-shrink-0 mt-0.5"></div>
                <div>
                  <p class="text-sm font-medium text-gray-800">{{ addr.name }} {{ addr.phone }} <span v-if="addr.is_default" class="text-xs bg-indigo-100 text-indigo-600 px-2 py-0.5 rounded-full ml-1">默认</span></p>
                  <p class="text-sm text-gray-600 mt-0.5">{{ addr.detail }}</p>
                </div>
              </div>
            </div>
          </div>
          <textarea v-model="address" placeholder="请输入收货地址" class="input-modern w-full" rows="2"></textarea>
        </div>

        <div class="flex flex-col sm:flex-row items-center justify-between bg-gray-900 text-white rounded-2xl p-6">
          <div class="text-sm text-gray-300 mb-3 sm:mb-0">
            共 {{ cart.reduce((sum, i) => sum + i.quantity, 0) }} 件商品
          </div>
          <div class="flex items-center space-x-6">
            <div class="text-right">
              <p class="text-sm text-gray-300">合计</p>
              <p class="text-2xl font-bold">¥{{ total }}</p>
            </div>
            <button @click="checkout" :disabled="submitting" class="btn-success py-3 px-8 text-base flex items-center space-x-2">
              <CreditCardIcon class="w-5 h-5" />
              <span>{{ submitting ? '提交中...' : '去结算' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api/axios'
import {
  ShoppingCartIcon,
  PhotoIcon,
  MinusIcon,
  PlusIcon,
  TrashIcon,
  MapPinIcon,
  CheckCircleIcon,
  CreditCardIcon,
} from '@heroicons/vue/24/outline'

const router = useRouter()
const cart = ref([])
const address = ref('')
const addresses = ref([])
const selectedAddress = ref(null)
const submitting = ref(false)
const baseUrl = 'http://127.0.0.1:8000'

function firstImage(product) {
  const images = product?.images || []
  const url = images[0] || product?.image_url || ''
  if (!url) return ''
  return url.startsWith('http') ? url : baseUrl + url
}

const total = computed(() => cart.value.reduce((sum, i) => sum + i.price * i.quantity, 0).toFixed(2))

function loadCart() {
  cart.value = JSON.parse(localStorage.getItem('cart') || '[]')
}

async function loadAddresses() {
  const res = await api.get('/addresses')
  addresses.value = res.data
  const defaultAddr = res.data.find(a => a.is_default)
  if (defaultAddr) {
    selectedAddress.value = defaultAddr
    address.value = `${defaultAddr.name} ${defaultAddr.phone} ${defaultAddr.detail}`
  }
}

function selectAddress(addr) {
  selectedAddress.value = addr
  address.value = `${addr.name} ${addr.phone} ${addr.detail}`
}

function changeQty(idx, delta) {
  cart.value[idx].quantity += delta
  if (cart.value[idx].quantity <= 0) cart.value.splice(idx, 1)
  saveCart()
}

function remove(idx) {
  cart.value.splice(idx, 1)
  saveCart()
}

function saveCart() {
  localStorage.setItem('cart', JSON.stringify(cart.value))
}

async function checkout() {
  if (cart.value.length === 0) return
  if (!address.value.trim()) {
    alert('请先填写收货地址')
    return
  }
  submitting.value = true
  try {
    const items = cart.value.map(i => ({ product_id: i.product_id, quantity: i.quantity, spec: i.spec }))
    await api.post('/orders/checkout', { items, address: address.value })
    localStorage.removeItem('cart')
    alert('下单成功')
    router.push('/orders')
  } catch (e) {
    alert(e.response?.data?.detail || '下单失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadCart()
  loadAddresses()
})
</script>
