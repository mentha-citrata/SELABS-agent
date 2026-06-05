<template>
  <WorkbenchShell
    :api-status="apiStatus"
    :busy="busy"
    :messages="messages"
    :recent-form="recentForm"
    :session-id="sessionId"
    @send="sendMessage"
    @form-submit="submitA2UIForm"
  />
</template>

<script>
import { reactive, ref } from 'vue'
import WorkbenchShell from './components/WorkbenchShell.vue'
import {
  createAgentSession,
  openAgentStream,
  sendAgentMessage
} from './services/agentStream'

function createId() {
  return globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function createMessage(role, content = '') {
  return {
    id: createId(),
    role,
    content,
    blocks: [],
    streaming: false
  }
}

export default {
  name: 'App',
  components: { WorkbenchShell },
  setup() {
    const apiStatus = ref('idle')
    const busy = ref(false)
    const messages = ref([])
    const recentForm = ref(null)
    const sessionId = ref('')

    let closeStream = null

    async function ensureSession() {
      if (!sessionId.value) {
        sessionId.value = await createAgentSession()
      }

      return sessionId.value
    }

    async function sendMessage(content) {
      if (busy.value) {
        return false
      }

      try {
        const session = await ensureSession()
        const userContent = typeof content === 'string' ? content : JSON.stringify(content, null, 2)
        messages.value.push(createMessage('user', userContent))
        return await startAgentTurn(session, content)
      } catch (error) {
        busy.value = false
        apiStatus.value = 'error'
        messages.value.push(createMessage('error', error.message))
        return false
      }
    }

    async function startAgentTurn(session, content) {
      busy.value = true
      apiStatus.value = 'streaming'

      const assistant = reactive(createMessage('assistant', ''))
      assistant.streaming = true
      messages.value.push(assistant)

      closeStream?.()
      closeStream = openAgentStream(session, {
        onEvent(event) {
          applyStreamEvent(assistant, event)
        },
        onDone() {
          assistant.streaming = false
          busy.value = false
          apiStatus.value = 'online'
        },
        onError(error) {
          assistant.streaming = false
          busy.value = false
          apiStatus.value = 'error'
          messages.value.push(createMessage('error', error.message))
        }
      })

      try {
        await sendAgentMessage(session, content)
        return true
      } catch (error) {
        closeStream?.()
        assistant.streaming = false
        busy.value = false
        apiStatus.value = 'error'
        messages.value.push(createMessage('error', error.message))
        return false
      }
    }

    function applyStreamEvent(assistant, event) {
      if (event.type === 'markdown_delta') {
        assistant.content += event.content
      }

      if (event.type === 'ui_block' && event.block) {
        assistant.blocks.push(event.block)
      }

      if (event.type === 'error') {
        messages.value.push(createMessage('error', event.message))
      }
    }

    async function submitA2UIForm({ block, payload, summary, onError, onSuccess }) {
      const accepted = await sendMessage(payload)

      if (!accepted) {
        onError?.('当前请求未发送成功，请稍后重试')
        return
      }

      recentForm.value = {
        title: block.title || block.id,
        summary: summary.map((row) => `${row.label}: ${row.value}`).join(' / ')
      }
      onSuccess?.()
    }

    return {
      apiStatus,
      busy,
      messages,
      recentForm,
      sendMessage,
      sessionId,
      submitA2UIForm
    }
  }
}
</script>
