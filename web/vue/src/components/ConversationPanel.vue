<template>
  <section class="conversation-panel" aria-label="对话">
    <div ref="scrollBox" class="conversation-panel__scroll">
      <div v-if="messages.length === 0" class="empty-state">
        <p class="eyebrow">CENTRAL LAB ENTRY</p>
        <h2>用对话管理实验室资源</h2>
        <p>可以查询机位、预约教室、查看设备和处理报修。Agent 会在需要时嵌入可提交表单。</p>
      </div>

      <MessageBubble
        v-for="(message, index) in messages"
        :key="message.id || index"
        :message="message"
        @form-submit="$emit('form-submit', $event)"
      />
    </div>

    <form class="input-dock" @submit.prevent="submit">
      <textarea
        v-model="draft"
        :disabled="isLoading"
        aria-label="输入实验室管理请求，例如：帮我预约明天下午的可用机位"
        placeholder="输入实验室管理请求..."
        rows="2"
        @keydown.enter.exact.prevent="submit"
      ></textarea>
      <button type="submit" :disabled="isLoading || !draft.trim()">
        {{ isLoading ? '响应中' : '发送' }}
      </button>
    </form>
  </section>
</template>

<script>
import { computed, nextTick, ref, watch } from 'vue'
import MessageBubble from './MessageBubble.vue'

export default {
  name: 'ConversationPanel',
  components: { MessageBubble },
  props: {
    busy: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    messages: {
      type: Array,
      default: () => []
    }
  },
  emits: ['form-submit', 'send'],
  setup(props, { emit }) {
    const draft = ref('')
    const isLoading = computed(() => props.busy || props.loading)
    const scrollBox = ref(null)

    function submit() {
      const text = draft.value.trim()
      if (!text || isLoading.value) return
      draft.value = ''
      emit('send', text)
    }

    watch(
      () => props.messages,
      () => nextTick(() => {
        if (scrollBox.value) {
          scrollBox.value.scrollTop = scrollBox.value.scrollHeight
        }
      }),
      { deep: true }
    )

    return { draft, isLoading, scrollBox, submit }
  }
}
</script>
