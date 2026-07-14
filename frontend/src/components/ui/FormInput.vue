<template>
  <div>
    <label v-if="label" class="block text-sm font-medium text-gray-700 mb-1.5">{{ label }}</label>
    <div class="relative">
      <component
        v-if="icon"
        :is="icon"
        class="w-5 h-5 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none"
      />
      <input
        v-if="type !== 'textarea'"
        :type="type"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        :placeholder="placeholder"
        :disabled="disabled"
        :step="step"
        :min="min"
        class="input-modern w-full"
        :class="[{ 'pl-11': icon, 'px-4': !icon }, inputClass]"
      />
      <textarea
        v-else
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        :placeholder="placeholder"
        :disabled="disabled"
        :rows="rows"
        class="input-modern w-full min-h-[100px] resize-y"
        :class="[{ 'pl-11': icon, 'px-4': !icon }, inputClass]"
      />
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: [String, Number], default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  label: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  icon: { type: [Object, Function], default: null },
  rows: { type: Number, default: 3 },
  step: { type: String, default: undefined },
  min: { type: [String, Number], default: undefined },
  inputClass: { type: String, default: '' },
})
defineEmits(['update:modelValue'])
</script>
