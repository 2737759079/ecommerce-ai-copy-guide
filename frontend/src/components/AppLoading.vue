<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div class="bg-white rounded-3xl shadow-2xl p-8 flex flex-col items-center space-y-4">
        <div class="relative w-16 h-16">
          <div class="absolute inset-0 rounded-full border-4 border-primary-light"></div>
          <div class="absolute inset-0 rounded-full border-4 border-primary border-t-transparent animate-spin"></div>
        </div>
        <p class="text-gray-700 font-medium">{{ message }}</p>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  message: { type: String, default: 'AI 正在生成中，请稍候...' },
})
</script>
