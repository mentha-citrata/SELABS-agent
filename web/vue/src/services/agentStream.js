export async function createAgentSession() {
  const response = await fetch('/api/agent/session', { method: 'POST' })

  if (!response.ok) {
    throw new Error(`创建会话失败: HTTP ${response.status}`)
  }

  const body = await response.json()

  if (!body.session_id) {
    throw new Error('创建会话失败: 响应缺少 session_id')
  }

  return body.session_id
}

export async function sendAgentMessage(sessionId, message) {
  const response = await fetch('/api/agent/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message })
  })

  if (!response.ok) {
    throw new Error(`发送失败: HTTP ${response.status}`)
  }

  return response.json()
}

export function openAgentStream(sessionId, handlers = {}) {
  const source = new EventSource(`/api/agent/stream?session_id=${encodeURIComponent(sessionId)}`)

  source.onmessage = (event) => {
    try {
      const payload = normalizeStreamEvent(JSON.parse(event.data))
      if (payload.type === 'error') {
        handlers.onError?.(new Error(payload.message))
        source.close()
        return
      }
      handlers.onEvent?.(payload)
    } catch (error) {
      handlers.onError?.(error)
      source.close()
    }
  }

  source.addEventListener('done', () => {
    handlers.onDone?.()
    source.close()
  })

  source.onerror = () => {
    handlers.onError?.(new Error('Agent stream disconnected'))
    source.close()
  }

  return () => source.close()
}

export function normalizeStreamEvent(event) {
  if (!event || typeof event !== 'object') {
    return { type: 'error', message: '收到无效的流事件' }
  }

  if (event.type === 'markdown_delta') {
    return {
      type: 'markdown_delta',
      message_id: event.message_id,
      content: event.content || ''
    }
  }

  if (event.type === 'ui_block') {
    return {
      type: 'ui_block',
      message_id: event.message_id,
      block: event.block
    }
  }

  if (event.type === 'message_start' || event.type === 'message_done') {
    return event
  }

  if (event.type === 'tool_status') {
    return {
      type: 'tool_status',
      status: event.status || 'running',
      label: event.label || '工具执行中'
    }
  }

  if (event.type === 'error') {
    return {
      type: 'error',
      message: event.message || 'Agent 响应失败'
    }
  }

  return {
    type: 'error',
    message: `未知流事件: ${event.type || 'unknown'}`
  }
}
