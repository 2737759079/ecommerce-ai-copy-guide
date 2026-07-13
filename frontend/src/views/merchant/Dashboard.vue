<template>
  <div class="fade-in-up">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-800 flex items-center space-x-2">
        <ChartPieIcon class="w-7 h-7 text-indigo-600" />
        <span>数据看板</span>
      </h2>
    </div>

    <!-- 日期选择 -->
    <div class="bg-white rounded-2xl shadow-md p-4 mb-6 flex gap-4 flex-wrap items-center">
      <label class="text-sm font-medium text-gray-600 flex items-center space-x-1">
        <CalendarIcon class="w-4 h-4" />
        <span>选择日期</span>
      </label>
      <input type="date" v-model="selectedDate" @change="loadData" class="input-modern w-auto text-sm py-2" />
      <button @click="setToday" class="btn-secondary text-sm py-2">今天</button>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
      <div v-for="(card, idx) in statCards" :key="card.key" class="relative overflow-hidden rounded-2xl p-5 text-white shadow-lg fade-in-up" :style="{ animationDelay: idx * 60 + 'ms', background: card.gradient }">
        <div class="absolute top-0 right-0 w-24 h-24 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2"></div>
        <div class="relative z-10">
          <div class="flex items-center space-x-2 opacity-90 mb-2">
            <component :is="card.icon" class="w-5 h-5" />
            <p class="text-sm">{{ card.label }}</p>
          </div>
          <p class="text-2xl font-bold count-up">{{ card.prefix }}{{ dashboard[card.key] }}</p>
        </div>
      </div>
    </div>

    <!-- 订单查询 -->
    <div class="bg-white rounded-2xl shadow-md p-6 mb-6">
      <h3 class="font-bold text-lg mb-4 flex items-center space-x-2">
        <MagnifyingGlassIcon class="w-5 h-5 text-indigo-600" />
        <span>订单查询</span>
      </h3>
      <div class="flex gap-3 flex-wrap mb-4">
        <div class="relative flex-1 min-w-[200px]">
          <MagnifyingGlassIcon class="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input v-model="query.keyword" placeholder="搜索订单号/用户昵称" class="input-modern pl-10 text-sm w-full" />
        </div>
        <select v-model="query.status" class="input-modern text-sm w-40">
          <option value="">全部状态</option>
          <option value="pending">待支付</option>
          <option value="paid">已支付</option>
          <option value="shipped">待收货</option>
          <option value="completed">已完成</option>
          <option value="refunded">已退款</option>
          <option value="cancelled">已取消</option>
        </select>
        <button @click="searchOrders" class="btn-primary text-sm px-5">查询</button>
      </div>
      <div class="overflow-x-auto rounded-xl border border-gray-100">
        <table class="table-modern">
          <thead>
            <tr><th class="px-4 py-3 rounded-tl-xl">订单号</th><th>用户</th><th>金额</th><th>状态</th><th>时间</th></tr>
          </thead>
          <tbody>
            <tr v-for="o in queryOrders" :key="o.id" class="border-b">
              <td class="px-4 py-3 font-mono text-sm">{{ o.order_no }}</td>
              <td>
                <div class="flex items-center space-x-2">
                  <div class="w-7 h-7 rounded-full bg-gradient-to-br from-indigo-400 to-pink-400 flex items-center justify-center text-white text-xs font-bold">{{ (o.user_nickname || 'U').charAt(0).toUpperCase() }}</div>
                  <div>
                    <p class="text-sm">{{ o.user_nickname }}</p>
                    <p class="text-xs text-gray-400">{{ o.user_display_id }}</p>
                  </div>
                </div>
              </td>
              <td class="font-semibold text-gray-700">¥{{ o.total_amount }}</td>
              <td><span :class="statusBadgeClass(o.status)">{{ statusText(o.status) }}</span></td>
              <td class="text-sm text-gray-500">{{ new Date(o.created_at).toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="queryOrders.length === 0" class="p-6 text-center text-gray-500">暂无查询结果</div>
      </div>
    </div>

    <!-- 当日最近订单 -->
    <div class="bg-white rounded-2xl shadow-md p-6">
      <h3 class="font-bold text-lg mb-4 flex items-center space-x-2">
        <ClockIcon class="w-5 h-5 text-indigo-600" />
        <span>当日最近订单</span>
      </h3>
      <div class="overflow-x-auto rounded-xl border border-gray-100">
        <table class="table-modern">
          <thead>
            <tr><th class="px-4 py-3 rounded-tl-xl">订单号</th><th>用户</th><th>金额</th><th>状态</th><th>时间</th></tr>
          </thead>
          <tbody>
            <tr v-for="o in dashboard.recent_orders" :key="o.id" class="border-b">
              <td class="px-4 py-3 font-mono text-sm">{{ o.order_no }}</td>
              <td>
                <div class="flex items-center space-x-2">
                  <div class="w-7 h-7 rounded-full bg-gradient-to-br from-indigo-400 to-pink-400 flex items-center justify-center text-white text-xs font-bold">{{ (o.user_nickname || 'U').charAt(0).toUpperCase() }}</div>
                  <div>
                    <p class="text-sm">{{ o.user_nickname }}</p>
                    <p class="text-xs text-gray-400">{{ o.user_display_id }}</p>
                  </div>
                </div>
              </td>
              <td class="font-semibold text-gray-700">¥{{ o.total_amount }}</td>
              <td><span :class="statusBadgeClass(o.status)">{{ statusText(o.status) }}</span></td>
              <td class="text-sm text-gray-500">{{ new Date(o.created_at).toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="dashboard.recent_orders.length === 0" class="p-6 text-center text-gray-500">当日暂无订单</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../../api/axios'
import {
  ChartPieIcon,
  CalendarIcon,
  BanknotesIcon,
  ShoppingCartIcon,
  ArrowPathIcon,
  XCircleIcon,
  MagnifyingGlassIcon,
  ClockIcon,
} from '@heroicons/vue/24/outline'

function formatDate(d) {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const selectedDate = ref(formatDate(new Date()))
const dashboard = ref({
  date: '',
  daily_amount: 0,
  monthly_amount: 0,
  daily_orders: 0,
  return_orders: 0,
  cancel_orders: 0,
  recent_orders: [],
})
const query = ref({ keyword: '', status: '' })
const queryOrders = ref([])

const statCards = computed(() => [
  { key: 'daily_amount', label: '当日成交额', prefix: '¥', icon: BanknotesIcon, gradient: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)' },
  { key: 'monthly_amount', label: '当月成交额', prefix: '¥', icon: BanknotesIcon, gradient: 'linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%)' },
  { key: 'daily_orders', label: '当日成交订单数', prefix: '', icon: ShoppingCartIcon, gradient: 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)' },
  { key: 'return_orders', label: '退货订单数', prefix: '', icon: ArrowPathIcon, gradient: 'linear-gradient(135deg, #f43f5e 0%, #e11d48 100%)' },
  { key: 'cancel_orders', label: '取消订单数', prefix: '', icon: XCircleIcon, gradient: 'linear-gradient(135deg, #f59e0b 0%, #ea580c 100%)' },
])

function statusText(status) {
  const map = { pending: '待支付', paid: '已支付', shipped: '待收货', completed: '已完成', cancelled: '已取消', refunded: '已退款' }
  return map[status] || status
}

function statusBadgeClass(status) {
  const map = { pending: 'badge-yellow', paid: 'badge-blue', shipped: 'badge-indigo', completed: 'badge-green', cancelled: 'badge-gray', refunded: 'badge-red' }
  return 'badge ' + (map[status] || 'badge-gray')
}

function setToday() {
  selectedDate.value = formatDate(new Date())
  loadData()
}

async function loadData() {
  const res = await api.get('/orders/dashboard', { params: { date_str: selectedDate.value } })
  dashboard.value = res.data
}

async function searchOrders() {
  const params = {}
  if (query.value.keyword) params.keyword = query.value.keyword
  if (query.value.status) params.status = query.value.status
  const res = await api.get('/orders/all/list', { params })
  queryOrders.value = res.data
}

onMounted(() => {
  loadData()
  searchOrders()
})
</script>
