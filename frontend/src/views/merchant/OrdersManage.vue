<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">订单管理</h2>
    <div class="bg-white rounded-xl shadow-sm p-4 mb-6 flex gap-4 flex-wrap">
      <input v-model="filter.keyword" placeholder="搜索订单号" class="border rounded-lg px-3 py-2 text-sm flex-1" />
      <select v-model="filter.status" class="border rounded-lg px-3 py-2 text-sm">
        <option value="">全部状态</option>
        <option value="pending">待支付</option>
        <option value="paid">已支付</option>
        <option value="shipped">待收货</option>
        <option value="completed">已完成</option>
        <option value="refunded">已退款</option>
        <option value="cancelled">已取消</option>
      </select>
      <button @click="loadOrders" class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700">搜索</button>
    </div>
    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm text-left">
        <thead class="bg-gray-50 text-gray-600">
          <tr>
            <th class="px-4 py-3">订单号</th>
            <th>用户</th>
            <th>商品</th>
            <th>金额</th>
            <th>地址</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.id" class="border-b hover:bg-gray-50">
            <td class="px-4 py-3">{{ order.order_no }}</td>
            <td>{{ order.user_nickname }}<br><span class="text-xs text-gray-400">{{ order.user_display_id }}</span></td>
            <td>
              <div v-for="item in order.items" :key="item.id" class="text-xs">{{ item.product_name }}<br><span class="text-gray-400">{{ item.product_display_id }} × {{ item.quantity }}</span></div>
            </td>
            <td>¥{{ order.total_amount }}</td>
            <td class="truncate max-w-xs">{{ order.address }}</td>
            <td>{{ statusText(order.status) }}</td>
            <td class="space-x-2">
              <button @click="editAddress(order)" class="text-indigo-600 hover:underline text-xs">改地址</button>
              <button @click="editStatus(order)" class="text-indigo-600 hover:underline text-xs">改状态</button>
              <button @click="confirmDelete(order)" class="text-red-500 hover:underline text-xs">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showAddress" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-full max-w-md">
        <h3 class="font-bold text-lg mb-4">修改地址</h3>
        <textarea v-model="editForm.address" rows="3" class="w-full border rounded-lg px-3 py-2"></textarea>
        <div class="mt-6 flex justify-end space-x-2">
          <button @click="showAddress = false" class="px-4 py-2 border rounded-lg">取消</button>
          <button @click="saveAddress" class="px-4 py-2 bg-indigo-600 text-white rounded-lg">保存</button>
        </div>
      </div>
    </div>

    <div v-if="showStatus" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-full max-w-md">
        <h3 class="font-bold text-lg mb-4">修改状态</h3>
        <select v-model="editForm.status" class="w-full border rounded-lg px-3 py-2">
          <option value="pending">待支付</option>
          <option value="paid">已支付</option>
          <option value="shipped">待收货</option>
          <option value="completed">已完成</option>
          <option value="refunded">已退款</option>
          <option value="cancelled">已取消</option>
        </select>
        <div class="mt-6 flex justify-end space-x-2">
          <button @click="showStatus = false" class="px-4 py-2 border rounded-lg">取消</button>
          <button @click="saveStatus" class="px-4 py-2 bg-indigo-600 text-white rounded-lg">保存</button>
        </div>
      </div>
    </div>

    <div v-if="showConfirm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-80">
        <h3 class="font-bold text-lg mb-4">确认删除</h3>
        <p class="text-sm text-gray-600 mb-4">删除订单将同步退回已支付资金并恢复库存，确定吗？</p>
        <div class="flex justify-end space-x-2">
          <button @click="showConfirm = false" class="px-4 py-2 border rounded-lg">取消</button>
          <button @click="doDelete" class="px-4 py-2 bg-red-500 text-white rounded-lg">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/axios'

const orders = ref([])
const filter = ref({ keyword: '', status: '' })
const showAddress = ref(false)
const showStatus = ref(false)
const showConfirm = ref(false)
const editForm = ref({ id: null, address: '', status: '' })
const confirmItem = ref(null)

function statusText(status) {
  const map = { pending: '待支付', paid: '已支付', shipped: '待收货', completed: '已完成', cancelled: '已取消', refunded: '已退款' }
  return map[status] || status
}

async function loadOrders() {
  const params = {}
  if (filter.value.keyword) params.keyword = filter.value.keyword
  if (filter.value.status) params.status = filter.value.status
  const res = await api.get('/orders/all/list', { params })
  orders.value = res.data
}

function editAddress(order) {
  editForm.value = { id: order.id, address: order.address, status: order.status }
  showAddress.value = true
}

async function saveAddress() {
  await api.put(`/orders/${editForm.value.id}/address`, null, { params: { address: editForm.value.address } })
  showAddress.value = false
  loadOrders()
}

function editStatus(order) {
  editForm.value = { id: order.id, address: order.address, status: order.status }
  showStatus.value = true
}

async function saveStatus() {
  await api.put(`/orders/${editForm.value.id}/status`, null, { params: { status: editForm.value.status } })
  showStatus.value = false
  loadOrders()
}

function confirmDelete(order) {
  confirmItem.value = order
  showConfirm.value = true
}

async function doDelete() {
  if (!confirmItem.value) return
  await api.delete(`/orders/${confirmItem.value.id}`, { params: { refund: true } })
  showConfirm.value = false
  confirmItem.value = null
  loadOrders()
}

onMounted(loadOrders)
</script>
