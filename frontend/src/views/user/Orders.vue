<template>
  <div class="max-w-4xl mx-auto fade-in-up">
    <div class="bg-white rounded-3xl shadow-lg p-6 md:p-8">
      <div class="flex items-center space-x-2 mb-6">
        <ClipboardDocumentListIcon class="w-6 h-6 text-primary" />
        <h2 class="text-2xl font-bold text-gray-800">我的订单</h2>
      </div>

      <div class="bg-gray-50 rounded-2xl p-4 mb-6 flex gap-3 flex-wrap items-end">
        <FormInput v-model="filter.keyword" label="搜索订单号" placeholder="请输入订单号" :icon="MagnifyingGlassIcon" class="flex-1 min-w-[200px]" />
        <FormSelect v-model="filter.status" label="订单状态" :icon="FunnelIcon" class="w-40">
          <option value="">全部状态</option>
          <option value="pending">待支付</option>
          <option value="paid">已支付</option>
          <option value="shipped">待收货</option>
          <option value="completed">已完成</option>
          <option value="refunded">已退款</option>
          <option value="cancelled">已取消</option>
        </FormSelect>
        <button @click="loadOrders" class="btn-primary text-sm px-5">
          <MagnifyingGlassIcon class="w-4 h-4 inline mr-1" />
          搜索
        </button>
      </div>

      <div v-if="orders.length === 0" class="text-center py-20">
        <div class="w-20 h-20 bg-primary-light rounded-full flex items-center justify-center mx-auto mb-4">
          <ClipboardDocumentListIcon class="w-10 h-10 text-primary/40" />
        </div>
        <p class="text-gray-500">暂无订单</p>
      </div>

      <div v-else class="space-y-4">
        <div v-for="order in orders" :key="order.id" class="relative bg-white border border-gray-100 rounded-2xl p-5 shadow-sm hover:shadow-md transition-shadow overflow-hidden">
          <div class="absolute left-0 top-0 bottom-0 w-1" :class="statusColor(order.status)"></div>
          <div class="flex justify-between items-center mb-3 pl-3">
            <div class="flex items-center space-x-2 text-sm text-gray-500">
              <span class="font-mono">{{ order.order_no }}</span>
              <span class="text-gray-300">|</span>
              <span>{{ new Date(order.created_at).toLocaleString() }}</span>
            </div>
            <span :class="statusBadgeClass(order.status)" class="badge">{{ statusText(order.status) }}</span>
          </div>
          <div class="pl-3 space-y-2">
            <div v-for="item in order.items" :key="item.id" class="flex justify-between items-center text-sm bg-gray-50 rounded-xl p-3">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center text-xs text-gray-400">{{ item.product_name.charAt(0) }}</div>
                <div>
                  <p class="font-medium text-gray-800">{{ item.product_name }}</p>
                  <p class="text-xs text-gray-500">{{ item.product_display_id }} × {{ item.quantity }}</p>
                </div>
              </div>
              <span class="font-semibold text-gray-700">¥{{ item.price }}</span>
            </div>
          </div>
          <p class="pl-3 text-sm text-gray-600 mt-3 flex items-start space-x-1">
            <MapPinIcon class="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
            <span>{{ order.recipient_name }} {{ order.recipient_phone }} {{ order.recipient_address || order.address }}</span>
          </p>
          <div class="pl-3 mt-4 flex flex-col sm:flex-row justify-between items-start sm:items-center border-t pt-4">
            <span class="font-bold text-lg text-gradient mb-3 sm:mb-0">合计：¥{{ order.total_amount }}</span>
            <div class="flex flex-wrap gap-2">
              <button v-if="order.status === 'pending'" @click="pay(order.id)" class="btn-success text-sm py-1.5 px-4 flex items-center space-x-1">
                <CreditCardIcon class="w-3.5 h-3.5" />
                <span>模拟支付</span>
              </button>
              <button v-if="['pending', 'paid'].includes(order.status)" @click="openShipping(order)" class="btn-primary text-sm py-1.5 px-4 flex items-center space-x-1">
                <PencilSquareIcon class="w-3.5 h-3.5" />
                <span>修改收货信息</span>
              </button>
              <button v-if="order.status === 'shipped'" @click="complete(order.id)" class="btn-primary text-sm py-1.5 px-4 flex items-center space-x-1">
                <CheckBadgeIcon class="w-3.5 h-3.5" />
                <span>确认收货</span>
              </button>
              <button v-if="['pending', 'paid'].includes(order.status)" @click="cancel(order.id)" class="btn-danger text-sm py-1.5 px-4 flex items-center space-x-1">
                <XCircleIcon class="w-3.5 h-3.5" />
                <span>取消订单</span>
              </button>
              <button v-if="order.status === 'completed'" @click="review(order)" class="btn-primary text-sm py-1.5 px-4 flex items-center space-x-1 bg-gradient-to-r from-yellow-500 to-orange-500 border-0">
                <StarIcon class="w-3.5 h-3.5" />
                <span>评价</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showReview" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md modal-in max-h-[90vh] overflow-y-auto">
        <h3 class="font-bold text-lg mb-4 flex items-center space-x-2">
          <StarIcon class="w-5 h-5 text-yellow-500" />
          <span>发表评价</span>
        </h3>
        <div class="mb-4">
          <FormSelect v-model="reviewForm.rating" label="评分" :icon="StarIcon">
            <option v-for="n in 5" :key="n" :value="n">{{ n }}星</option>
          </FormSelect>
        </div>
        <div class="mb-4">
          <FormInput v-model="reviewForm.content" label="评价内容" type="textarea" :rows="3" placeholder="请输入评价内容" :icon="ChatBubbleLeftIcon" />
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1.5">上传图片</label>
          <input type="file" multiple accept="image/*" @change="handleReviewImages" class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary-light file:text-primary-dark hover:file:bg-primary-light" />
          <div v-if="reviewImagePreviews.length" class="flex flex-wrap gap-2 mt-2">
            <img v-for="(img, idx) in reviewImagePreviews" :key="idx" :src="img" class="w-16 h-16 object-cover rounded-lg border" />
          </div>
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1.5">上传视频</label>
          <input type="file" accept="video/*" @change="handleReviewVideo" class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary-light file:text-primary-dark hover:file:bg-primary-light" />
          <video v-if="reviewVideoPreview" :src="reviewVideoPreview" controls class="mt-2 h-32 rounded-lg"></video>
        </div>
        <div class="flex justify-end space-x-2">
          <button @click="showReview = false" class="btn-secondary text-sm">取消</button>
          <button @click="submitReview" class="btn-primary text-sm">提交</button>
        </div>
      </div>
    </div>

    <div v-if="showShipping" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md modal-in">
        <h3 class="font-bold text-lg mb-4 flex items-center space-x-2">
          <MapPinIcon class="w-5 h-5 text-primary" />
          <span>修改收货信息</span>
        </h3>
        <div class="space-y-3">
          <FormInput v-model="shippingForm.name" label="收件人姓名" placeholder="请输入收件人姓名" :icon="UserIcon" />
          <FormInput v-model="shippingForm.phone" label="手机号" placeholder="请输入手机号" :icon="PhoneIcon" />
          <FormInput v-model="shippingForm.address" label="详细地址" type="textarea" :rows="2" placeholder="请输入详细地址" :icon="MapPinIcon" />
        </div>
        <div class="mt-6 flex justify-end space-x-2">
          <button @click="showShipping = false" class="btn-secondary text-sm">取消</button>
          <button @click="saveShipping" class="btn-primary text-sm">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/axios'
import FormInput from '../../components/ui/FormInput.vue'
import FormSelect from '../../components/ui/FormSelect.vue'
import {
  ClipboardDocumentListIcon,
  MagnifyingGlassIcon,
  MapPinIcon,
  CreditCardIcon,
  CheckBadgeIcon,
  XCircleIcon,
  StarIcon,
  PencilSquareIcon,
  UserIcon,
  PhoneIcon,
  ChatBubbleLeftIcon,
  FunnelIcon,
} from '@heroicons/vue/24/outline'

const orders = ref([])
const filter = ref({ keyword: '', status: '' })
const showReview = ref(false)
const showShipping = ref(false)
const reviewForm = ref({ order_id: null, product_id: null, rating: 5, content: '' })
const reviewImages = ref([])
const reviewImagePreviews = ref([])
const reviewVideo = ref(null)
const reviewVideoPreview = ref('')
const shippingForm = ref({ id: null, name: '', phone: '', address: '' })

function statusText(status) {
  const map = { pending: '待支付', paid: '已支付', shipped: '待收货', completed: '已完成', cancelled: '已取消', refunded: '已退款' }
  return map[status] || status
}

function statusColor(status) {
  const map = { pending: 'bg-yellow-400', paid: 'bg-blue-500', shipped: 'bg-primary-light0', completed: 'bg-green-500', cancelled: 'bg-gray-400', refunded: 'bg-red-400' }
  return map[status] || 'bg-gray-300'
}

function statusBadgeClass(status) {
  const map = {
    pending: 'badge-yellow',
    paid: 'badge-blue',
    shipped: 'badge-indigo',
    completed: 'badge-green',
    cancelled: 'badge-gray',
    refunded: 'badge-red',
  }
  return map[status] || 'badge-gray'
}

async function loadOrders() {
  const params = {}
  if (filter.value.keyword) params.keyword = filter.value.keyword
  if (filter.value.status) params.status = filter.value.status
  const res = await api.get('/orders/my', { params })
  orders.value = res.data
}

async function pay(id) {
  await api.post(`/orders/${id}/pay`, {}, { params: { method: 'wechat' } })
  loadOrders()
}

async function complete(id) {
  await api.post(`/orders/${id}/complete`)
  loadOrders()
}

async function cancel(id) {
  if (!confirm('取消订单将退回已支付资金，确定吗？')) return
  await api.post(`/orders/${id}/cancel`)
  loadOrders()
}

function review(order) {
  reviewForm.value.order_id = order.id
  reviewForm.value.product_id = order.items[0]?.product_id
  reviewForm.value.rating = 5
  reviewForm.value.content = ''
  reviewImages.value = []
  reviewImagePreviews.value = []
  reviewVideo.value = null
  reviewVideoPreview.value = ''
  showReview.value = true
}

function handleReviewImages(e) {
  const files = Array.from(e.target.files)
  reviewImages.value = files
  reviewImagePreviews.value = files.map(f => URL.createObjectURL(f))
}

function handleReviewVideo(e) {
  const file = e.target.files[0]
  reviewVideo.value = file || null
  reviewVideoPreview.value = file ? URL.createObjectURL(file) : ''
}

async function submitReview() {
  const formData = new FormData()
  formData.append('product_id', reviewForm.value.product_id)
  if (reviewForm.value.order_id) formData.append('order_id', reviewForm.value.order_id)
  formData.append('rating', reviewForm.value.rating)
  formData.append('content', reviewForm.value.content)
  reviewImages.value.forEach(f => formData.append('images', f))
  if (reviewVideo.value) formData.append('video', reviewVideo.value)
  await api.post('/reviews', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  showReview.value = false
  alert('评价成功')
  loadOrders()
}

function openShipping(order) {
  shippingForm.value = {
    id: order.id,
    name: order.recipient_name || '',
    phone: order.recipient_phone || '',
    address: order.recipient_address || order.address || '',
  }
  showShipping.value = true
}

async function saveShipping() {
  await api.put(`/orders/${shippingForm.value.id}/shipping`, null, {
    params: {
      name: shippingForm.value.name,
      phone: shippingForm.value.phone,
      address: shippingForm.value.address,
    }
  })
  showShipping.value = false
  loadOrders()
}

onMounted(loadOrders)
</script>
