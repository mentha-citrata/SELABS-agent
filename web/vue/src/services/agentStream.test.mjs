import test from 'node:test'
import assert from 'node:assert/strict'
import { normalizeStreamEvent } from './agentStream.js'

test('normalizeStreamEvent preserves backend error messages', () => {
  const event = normalizeStreamEvent({ type: 'error', message: 'backend failed' })

  assert.deepEqual(event, {
    type: 'error',
    message: 'backend failed'
  })
})

test('normalizeStreamEvent returns error for unknown events', () => {
  const event = normalizeStreamEvent({ type: 'surprise' })

  assert.equal(event.type, 'error')
  assert.equal(event.message, '未知流事件: surprise')
})
