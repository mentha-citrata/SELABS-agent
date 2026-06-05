<template>
  <aside class="context-panel">
    <section>
      <p class="eyebrow">SESSION</p>
      <h3>{{ sessionId ? '会话已建立' : '等待连接' }}</h3>
      <p>{{ sessionId || '尚未创建 Agent session' }}</p>
    </section>

    <section>
      <p class="eyebrow">AGENT API</p>
      <div class="status-line">
        <span class="status-light" :class="apiStatus"></span>
        <strong>{{ apiStatusLabel }}</strong>
      </div>
    </section>

    <section>
      <p class="eyebrow">RECENT FORM</p>
      <div v-if="recentForm">
        <h3>{{ recentForm.title }}</h3>
        <p>{{ recentForm.summary }}</p>
      </div>
      <p v-else>暂无表单提交</p>
    </section>

    <section>
      <p class="eyebrow">QUICK REQUESTS</p>
      <button
        v-for="item in quickRequests"
        :key="item"
        type="button"
        :disabled="busy"
        @click="$emit('quick-request', item)"
      >
        {{ item }}
      </button>
    </section>
  </aside>
</template>

<script>
export default {
  name: 'ContextPanel',
  props: {
    apiStatus: {
      type: String,
      default: 'idle'
    },
    busy: {
      type: Boolean,
      default: false
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
  emits: ['quick-request'],
  data() {
    return {
      quickRequests: [
        '查询可用机位',
        '预约教室',
        '查看我的预约',
        '查询设备借用状态',
        '预约机位表单'
      ]
    }
  },
  computed: {
    apiStatusLabel() {
      if (this.apiStatus === 'online') return 'ONLINE'
      if (this.apiStatus === 'error') return 'ERROR'
      if (this.apiStatus === 'streaming') return 'STREAMING'
      return 'IDLE'
    }
  }
}
</script>
