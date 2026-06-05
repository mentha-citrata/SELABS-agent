<template>
  <form class="a2ui-form" @submit.prevent="handleSubmit">
    <div class="a2ui-form__header">
      <div>
        <p class="eyebrow">A2UI FORM</p>
        <h3>{{ block.title || '操作表单' }}</h3>
      </div>
      <span class="status-pill" :class="{ submitted }">{{ statusLabel }}</span>
    </div>

    <p v-if="block.description" class="a2ui-form__description">{{ block.description }}</p>

    <div v-if="submitted" class="a2ui-summary">
      <div v-for="row in summaryRows" :key="row.label" class="a2ui-summary__row">
        <span>{{ row.label }}</span>
        <strong>{{ row.value }}</strong>
      </div>
    </div>

    <div v-else class="a2ui-fields">
      <input
        v-for="field in hiddenFields"
        :key="field.name"
        v-model="values[field.name]"
        :name="field.name"
        type="hidden"
      />

      <label v-for="field in visibleFields" :key="field.name" class="a2ui-field" :for="fieldId(field)">
        <span>
          {{ field.label || field.name }}
          <b v-if="field.required">*</b>
        </span>

        <select
          v-if="field.type === 'select'"
          :id="fieldId(field)"
          v-model="values[field.name]"
          :aria-describedby="errors[field.name] ? `${fieldId(field)}-error` : undefined"
          :aria-invalid="Boolean(errors[field.name])"
          :name="field.name"
          @change="clearError(field.name)"
        >
          <option value="" disabled>{{ field.placeholder || '请选择' }}</option>
          <option
            v-for="option in fieldOptions(field)"
            :key="optionValue(option)"
            :value="optionValue(option)"
          >
            {{ optionLabel(option) }}
          </option>
        </select>

        <textarea
          v-else-if="field.type === 'textarea'"
          :id="fieldId(field)"
          v-model="values[field.name]"
          :aria-describedby="errors[field.name] ? `${fieldId(field)}-error` : undefined"
          :aria-invalid="Boolean(errors[field.name])"
          :name="field.name"
          :placeholder="field.placeholder"
          rows="3"
          @input="clearError(field.name)"
        ></textarea>

        <input
          v-else-if="field.type === 'checkbox'"
          :id="fieldId(field)"
          v-model="values[field.name]"
          :aria-describedby="errors[field.name] ? `${fieldId(field)}-error` : undefined"
          :aria-invalid="Boolean(errors[field.name])"
          class="a2ui-checkbox"
          :name="field.name"
          type="checkbox"
          @change="clearError(field.name)"
        />

        <input
          v-else
          :id="fieldId(field)"
          v-model="values[field.name]"
          :aria-describedby="errors[field.name] ? `${fieldId(field)}-error` : undefined"
          :aria-invalid="Boolean(errors[field.name])"
          :name="field.name"
          :placeholder="field.placeholder"
          :type="inputType(field.type)"
          @input="clearError(field.name)"
        />

        <small v-if="errors[field.name]" :id="`${fieldId(field)}-error`">{{ errors[field.name] }}</small>
      </label>
    </div>

    <div v-if="!submitted" class="a2ui-actions">
      <p v-if="formError" class="a2ui-form__error">{{ formError }}</p>
      <button type="submit" :disabled="pending">{{ pending ? '提交中' : block.submitLabel || '提交' }}</button>
    </div>
  </form>
</template>

<script>
import { computed, reactive, ref, watch } from 'vue'
import {
  createFormSubmitMessage,
  createInitialValues,
  summarizeFormValues,
  validateForm
} from '../utils/a2ui'

export default {
  name: 'A2UIForm',
  props: {
    block: {
      type: Object,
      required: true
    }
  },
  emits: ['submit'],
  setup(props, { emit }) {
    const values = reactive({})
    const errors = reactive({})
    const formError = ref('')
    const pending = ref(false)
    const submitted = ref(false)
    const submittedSummary = ref([])

    const hiddenFields = computed(() => (props.block.fields || []).filter((field) => field.type === 'hidden'))
    const statusLabel = computed(() => {
      if (submitted.value) return '已提交'
      if (pending.value) return '提交中'
      return '待填写'
    })
    const visibleFields = computed(() => (props.block.fields || []).filter((field) => field.type !== 'hidden'))
    const summaryRows = computed(() => submittedSummary.value)

    watch(
      () => props.block,
      (block) => {
        resetValues(block)
      },
      { immediate: true }
    )

    function resetValues(block) {
      Object.keys(values).forEach((key) => delete values[key])
      Object.assign(values, createInitialValues(block))
      Object.keys(errors).forEach((key) => delete errors[key])
      formError.value = ''
      pending.value = false
      submitted.value = false
      submittedSummary.value = []
    }

    function fieldId(field) {
      return `${props.block.id || 'a2ui-form'}-${field.name}`
    }

    function fieldOptions(field) {
      return field.options || field.choices || []
    }

    function optionValue(option) {
      return typeof option === 'object' && option !== null ? option.value : option
    }

    function optionLabel(option) {
      return typeof option === 'object' && option !== null ? option.label || option.value : option
    }

    function clearError(fieldName) {
      if (!errors[fieldName]) return
      delete errors[fieldName]
    }

    function inputType(type) {
      if (type === 'datetime') return 'datetime-local'
      if (type === 'date') return 'date'
      if (type === 'number') return 'number'
      return 'text'
    }

    function handleSubmit() {
      if (pending.value) return

      Object.keys(errors).forEach((key) => delete errors[key])
      formError.value = ''
      const result = validateForm(props.block, values)

      if (!result.valid) {
        Object.assign(errors, result.errors)
        return
      }

      const payload = createFormSubmitMessage(props.block, values)
      const summary = summarizeFormValues(props.block, values)

      pending.value = true
      emit('submit', {
        block: props.block,
        payload,
        summary,
        onError(message) {
          pending.value = false
          formError.value = message || '提交失败，请稍后重试'
        },
        onSuccess() {
          submittedSummary.value = summary
          submitted.value = true
          pending.value = false
          formError.value = ''
        }
      })
    }

    return {
      clearError,
      errors,
      fieldId,
      fieldOptions,
      formError,
      handleSubmit,
      hiddenFields,
      inputType,
      optionLabel,
      optionValue,
      pending,
      statusLabel,
      submitted,
      summaryRows,
      values,
      visibleFields
    }
  }
}
</script>
