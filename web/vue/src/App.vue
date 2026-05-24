<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center p-6">
    <div class="w-full max-w-3xl">
      <header class="mb-4">
        <h1 class="text-2xl font-semibold text-slate-800">SELABS Agent</h1>
        <p class="text-sm text-slate-500">轻量演示：SSE 流式输出聊天界面</p>
      </header>

      <Chat />
    </div>
  </div>
</template>

<script>
import Chat from './components/Chat.vue'
export default { components: { Chat } }
</script>
