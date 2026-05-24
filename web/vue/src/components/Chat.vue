<template>
  <div class="bg-white shadow rounded-lg overflow-hidden">
    <div class="p-4 border-b">
      <div class="text-sm text-slate-600">交互示例（支持流式输出）</div>
    </div>

    <div class="h-80 overflow-auto p-4 space-y-3 bg-gray-50" ref="box">
      <div v-for="(m, i) in messages" :key="i" :class="m.role === 'user' ? 'text-right' : ''">
        <div :class="['inline-block p-3 rounded-lg', m.role === 'user' ? 'bg-indigo-100 text-indigo-900' : 'bg-white text-slate-800']">
          <div v-html="m.text"></div>
        </div>
      </div>
    </div>

    <div class="p-4 border-t flex items-center gap-3">
      <input v-model="input" @keydown.enter="send" class="flex-1 p-2 border rounded" placeholder="输入你的问题" />
      <button @click="send" class="px-4 py-2 bg-indigo-600 text-white rounded">发送</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'

export default {
  setup(){
    const input = ref('')
    const messages = ref([])
    const box = ref(null)

    function append(role, text){
      messages.value.push({role, text})
      nextTick(()=>{ if(box.value) box.value.scrollTop = box.value.scrollHeight })
    }

    async function createSession(){
      const r = await fetch('/api/agent/session', {method:'POST'})
      const j = await r.json()
      return j.session_id
    }

    async function send(){
      if(!input.value.trim()) return
      const text = input.value
      input.value = ''
      append('user', text)

      const sessionId = await createSession()

      const es = new EventSource(`/api/agent/stream?session_id=${sessionId}`)
      let partial = ''
      es.onmessage = (e)=>{
        try{
          const d = JSON.parse(e.data)
          partial += d.data
          // render or replace assistant last
          const idx = messages.value.findIndex(m=>m.role==='assistant' && m.partial)
          if(idx === -1){
            messages.value.push({role:'assistant', text: partial, partial: true})
          }else{
            messages.value[idx].text = partial
          }
        }catch(err){ console.warn(err) }
      }
      es.addEventListener('done', ()=>{ es.close(); if(messages.value.length) messages.value[messages.value.length-1].partial = false })
      es.onerror = ()=>{ es.close(); }

      // trigger agent processing
      await fetch('/api/agent/send', {
        method: 'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({session_id: sessionId, message: text})
      })
    }

    return { input, messages, send, box }
  }
}
</script>

<style scoped>
.bg-white { background: white }
</style>
