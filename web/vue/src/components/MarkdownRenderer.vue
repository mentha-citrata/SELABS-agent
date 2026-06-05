<template>
  <div class="markdown-body" v-html="html"></div>
</template>

<script>
import { computed } from 'vue'
import { renderMarkdown } from '../utils/markdown'

export default {
  name: 'MarkdownRenderer',
  props: {
    content: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    const html = computed(() => renderMarkdown(props.content))

    return { html }
  }
}
</script>
