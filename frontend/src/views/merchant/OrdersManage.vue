<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">订单管理</h2>
    <div class="bg-white rounded-xl shadow-sm p-4 mb-6 flex gap-4 flex-wrap items-end">
      <FormInput v-model="filter.keyword" label="订单号" :icon="MagnifyingGlassIcon" placeholder="请输入订单号" class="flex-1 min-w-[200px]" />
      <FormSelect v-model="filter.status" label="订单状态" :icon="AdjustmentsHorizontalIcon" class="w-40">
        <option value="">全部状态</option>
        <option value="pending">待支付</option>
        <option value="paid">已支付</option>
        <option value="shipped">待收货</option>
        <option value="completed">已完成</option>
        <option value="refunded">已退款</option>
        <option value="cancelled">已取消</option>
      </FormSelect>
      <button @click="loadOrders" class="bg-primary text-white px-4 py-2 rounded-lg text-sm hover:bg-primary-dark">搜索</button>
    </div>
    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm text-left">
        <thead class="bg-gray-50 text-gray-600">
          <tr>
            <th class="px-4 py-3">订单号</th>
            <th>用户</th>
            <th>商品/数量</th>
            <th>购买件数</th>
            <th>金额</th>
            <th>收货信息</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.id" class="border-b hover:bg-gray-50">
            <td class="px-4 py-3">{{ order.order_no }}</td>
            <td>{{ order.user_nickname }}<br><span class="text-xs text-gray-400">{{ order.user_display_id }}</span></td>
            <td>
              <div v-for="item in order.items" :key="item.id" class="text-xs mb-1 last:mb-0">
                {{ item.product_name }}<br><span class="text-gray-400">{{ item.product_display_id }} × {{ item.quantity }}</span>
              </div>
            </td>
            <td>
              <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-primary-light text-primary-dark">
                <ShoppingCartIcon class="w-3.5 h-3.5 mr-1" />
                {{ order.items.reduce((s, i) => s + i.quantity, 0) }} 件
              </span>
            </td>
            <td>¥{{ order.total_amount }}</td>
            <td class="truncate max-w-xs">
              <p class="text-xs">{{ order.recipient_name }} {{ order.recipient_phone }}</p>
              <p class="text-xs text-gray-500">{{ order.recipient_address || order.address }}</p>
            </td>
            <td>{{ statusText(order.status) }}</td>
            <td class="space-x-2">
              <button @click="editShipping(order)" class="text-primary hover:underline text-xs">改收货信息</button>
              <button @click="editStatus(order)" class="text-primary hover:underline text-xs">改状态</button>
              <button @click="confirmDelete(order)" class="text-red-500 hover:underline text-xs">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showShipping" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-full max-w-md">
        <h3 class="font-bold text-lg mb-4">修改收货信息</h3>
        <div class="space-y-3">
          <FormInput v-model="shippingForm.name" label="收件人姓名" :icon="UserIcon" placeholder="请输入收件人姓名" />
          <FormInput v-model="shippingForm.phone" label="手机号" :icon="PhoneIcon" placeholder="请输入手机号" />
          <FormInput v-model="shippingForm.address" label="详细地址" :icon="MapPinIcon" type="textarea" :rows="2" placeholder="请输入详细地址" />
        </div>
        <div class="mt-6 flex justify-end space-x-2">
          <button @click="showShipping = false" class="px-4 py-2 border rounded-lg">取消</button>
          <button @click="saveShipping" class="px-4 py-2 bg-primary text-white rounded-lg">保存</button>
        </div>
      </div>
    </div>

    <div v-if="showStatus" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-full max-w-md">
        <h3 class="font-bold text-lg mb-4">修改状态</h3>
        <FormSelect v-model="editForm.status" label="订单状态" :icon="AdjustmentsHorizontalIcon" class="w-full">
          <option value="pending">待支付</option>
          <option value="paid">已支付</option>
          <option value="shipped">待收货</option>
          <option value="completed">已完成</option>
          <option value="refunded">已退款</option>
          <option value="cancelled">已取消</option>
        </FormSelect>
        <div class="mt-6 flex justify-end space-x-2">
          <button @click="showStatus = false" class="px-4 py-2 border rounded-lg">取消</button>
          <button @click="saveStatus" class="px-4 py-2 bg-primary text-white rounded-lg">保存</button>
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
import FormInput from '../../components/ui/FormInput.vue'
import FormSelect from '../../components/ui/FormSelect.vue'
import { MagnifyingGlassIcon, AdjustmentsHorizontalIcon, UserIcon, PhoneIcon, MapPinIcon, ShoppingCartIcon } from '@heroicons/vue/24/outline'

const orders = ref([])
const filter = ref({ keyword: '', status: '' })
const showShipping = ref(false)
const showStatus = ref(false)
const showConfirm = ref(false)
const shippingForm = ref({ id: null, name: '', phone: '', address: '' })
const editForm = ref({ id: null, status: '' })
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

function editShipping(order) {
  shippingForm.value = {
    id: order.id,
    name: order.recipient_name || '',
    phone: order.recipient_phone || '',
    address: order.recipient_address || order.address || '',
  }
  showShipping.value = true
}

async function saveShipping() {
  await api.put(`/orders/${shippingForm.value.id}/address`, null, {
    params: {
      name: shippingForm.value.name,
      phone: shippingForm.value.phone,
      address: shippingForm.value.address,
    }
  })
  showShipping.value = false
  loadOrders()
}

function editStatus(order) {
  editForm.value = { id: order.id, status: order.status }
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
