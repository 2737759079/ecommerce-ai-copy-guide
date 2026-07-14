<template>
  <div>
    <label v-if="label" class="block text-sm font-medium text-gray-700 mb-1.5">{{ label }}</label>
    <div class="relative">
      <component
        v-if="icon"
        :is="icon"
        class="w-5 h-5 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none"
      />
      <select
        :value="modelValue"
        @change="handleChange"
        :disabled="disabled"
        class="input-modern w-full appearance-none cursor-pointer"
        :class="[{ 'pl-11': icon, 'px-4': !icon }, selectClass]"
      >
        <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
        <slot />
      </select>
      <ChevronDownIcon class="w-4 h-4 text-gray-400 absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
    </div>
  </div>
</template>

<script setup>
import { ChevronDownIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  modelValue: { type: [String, Number, null], default: '' },
  disabled: { type: Boolean, default: false },
  icon: { type: [Object, Function], default: null },
  label: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  selectClass: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

function handleChange(e) {
  const selected = e.target.selectedOptions[0]
  // Vue stores the actual bound value on option._value; use it to preserve null/number
  const value = selected?._value !== undefined ? selected._value : e.target.value
  emit('update:modelValue', value)
}
</script>
