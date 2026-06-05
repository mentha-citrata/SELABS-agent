<template>
  <main class="workbench-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">SELABS AGENT</p>
        <h1>实验室管理中控入口</h1>
      </div>
      <div class="topbar__status">
        <span class="status-light" :class="apiStatus"></span>
        <span>{{ apiStatus }}</span>
      </div>
    </header>

    <div class="workbench-grid">
      <ConversationPanel
        :busy="busy"
        :messages="messages"
        @form-submit="$emit('form-submit', $event)"
        @send="$emit('send', $event)"
      />
      <ContextPanel
        :api-status="apiStatus"
        :busy="busy"
        :recent-form="recentForm"
        :session-id="sessionId"
        @quick-request="$emit('send', $event)"
      />
    </div>
  </main>
</template>

<script>
import ContextPanel from './ContextPanel.vue'
import ConversationPanel from './ConversationPanel.vue'

export default {
  name: 'WorkbenchShell',
  components: { ContextPanel, ConversationPanel },
  props: {
    apiStatus: {
      type: String,
      default: 'idle'
    },
    busy: {
      type: Boolean,
      default: false
    },
    messages: {
      type: Array,
      default: () => []
    },
    recentForm: {
      type: Object,
      default: null
    },
    sessionId: {
      type: String,
      default: ''
    }
  },
  emits: ['form-submit', 'send']
}
</script>
