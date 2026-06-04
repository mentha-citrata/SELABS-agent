import test from 'node:test'
import assert from 'node:assert/strict'
import {
  createInitialValues,
  validateForm,
  createFormSubmitMessage,
  summarizeFormValues
} from './a2ui.js'

const form = {
  kind: 'form',
  id: 'seat_reservation_001',
  title: '预约机位',
  fields: [
    { name: 'roomName', label: '房间', type: 'select', required: true, options: ['A101'] },
    { name: 'seatId', label: '机位 ID', type: 'number', required: true },
    { name: 'notes', label: '备注', type: 'textarea' },
    { name: 'urgent', label: '紧急', type: 'checkbox' }
  ]
}

test('createInitialValues builds stable defaults by field type', () => {
  assert.deepEqual(createInitialValues(form), {
    roomName: '',
    seatId: '',
    notes: '',
    urgent: false
  })
})

test('validateForm returns field errors for required empty values', () => {
  const result = validateForm(form, createInitialValues(form))
  assert.equal(result.valid, false)
  assert.deepEqual(result.errors, {
    roomName: '请选择或填写房间',
    seatId: '请选择或填写机位 ID'
  })
})

test('validateForm rejects required empty arrays and unchecked checkboxes', () => {
  const requiredForm = {
    kind: 'form',
    id: 'safety',
    fields: [
      { name: 'equipment', label: '设备', type: 'select', required: true },
      { name: 'confirmed', label: '确认安全规范', type: 'checkbox', required: true }
    ]
  }

  const result = validateForm(requiredForm, { equipment: [], confirmed: false })

  assert.equal(result.valid, false)
  assert.deepEqual(result.errors, {
    equipment: '请选择或填写设备',
    confirmed: '请选择或填写确认安全规范'
  })
})

test('createFormSubmitMessage wraps values for Agent', () => {
  const message = createFormSubmitMessage(form, { roomName: 'A101', seatId: 12 })
  assert.equal(message.kind, 'a2ui_form_submit')
  assert.equal(message.form_id, 'seat_reservation_001')
  assert.deepEqual(message.values, { roomName: 'A101', seatId: 12 })
})

test('summarizeFormValues uses labels and readable checkbox values', () => {
  const rows = summarizeFormValues(form, { roomName: 'A101', seatId: 12, urgent: true })
  assert.deepEqual(rows, [
    { label: '房间', value: 'A101' },
    { label: '机位 ID', value: 12 },
    { label: '备注', value: '' },
    { label: '紧急', value: '是' }
  ])
})
