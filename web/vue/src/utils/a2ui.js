export function createInitialValues(block) {
  return (block.fields || []).reduce((values, field) => {
    values[field.name] = field.type === 'checkbox' ? Boolean(field.defaultValue) : (field.defaultValue ?? '')
    return values
  }, {})
}

export function validateForm(block, values) {
  const errors = {}

  for (const field of block.fields || []) {
    if (!field.required) continue

    const value = values[field.name]
    const emptyString = typeof value === 'string' && value.trim() === ''
    const emptyArray = Array.isArray(value) && value.length === 0
    const uncheckedRequiredBox = field.type === 'checkbox' && value !== true
    const missing = value === undefined || value === null || emptyString || emptyArray || uncheckedRequiredBox

    if (missing) {
      errors[field.name] = `请选择或填写${field.label || field.name}`
    }
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors
  }
}

export function createFormSubmitMessage(block, values) {
  return {
    kind: 'a2ui_form_submit',
    form_id: block.id,
    values: { ...values }
  }
}

export function summarizeFormValues(block, values) {
  return (block.fields || [])
    .filter((field) => field.type !== 'hidden')
    .map((field) => ({
      label: field.label || field.name,
      value: formatFieldValue(field, values[field.name])
    }))
}

function formatFieldValue(field, value) {
  if (field.type === 'checkbox') {
    return value ? '是' : '否'
  }

  if (Array.isArray(value)) {
    return value.join(', ')
  }

  return value ?? ''
}
