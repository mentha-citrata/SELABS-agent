<template>
  <article class="message" :class="roleClass">
    <div class="message__meta">
      <span>{{ label }}</span>
      <span v-if="message.streaming" class="pulse-dot" aria-label="正在流式响应"></span>
    </div>

    <div class="message__body">
      <template v-if="isAssistant">
        <MarkdownRenderer v-if="contentText" :content="contentText" />
        <div v-if="uiBlocks.length" class="message__blocks">
          <A2UIForm
            v-for="(block, index) in uiBlocks"
            :key="block.id || index"
            :block="block"
            @submit="$emit('form-submit', $event)"
          />
        </div>
      </template>

      <pre v-else-if="isObjectContent">{{ formattedContent }}</pre>
      <p v-else>{{ contentText }}</p>
    </div>
  </article>
</template>

<script>
import A2UIForm from './A2UIForm.vue'
import MarkdownRenderer from './MarkdownRenderer.vue'

export default {
  name: 'MessageBubble',
  components: { A2UIForm, MarkdownRenderer },
  props: {
    message: {
      type: Object,
      required: true
    }
  },
  emits: ['form-submit'],
  computed: {
    contentText() {
      const content = this.message.content ?? this.message.text ?? ''
      return typeof content === 'string' ? content : JSON.stringify(content, null, 2)
    },
    formattedContent() {
      return JSON.stringify(this.message.content, null, 2)
    },
    isAssistant() {
      return this.message.role === 'assistant'
    },
    isObjectContent() {
      return this.message.content !== null && typeof this.message.content === 'object'
    },
    label() {
      if (this.message.role === 'user') return 'USER'
      if (this.message.role === 'system') return 'SYSTEM'
      if (this.message.role === 'error') return 'ERROR'
      return 'AGENT'
    },
    roleClass() {
      return `message--${this.message.role || 'assistant'}`
    },
    uiBlocks() {
      return this.message.uiBlocks || this.message.blocks || []
    }
  }
}
</script>
