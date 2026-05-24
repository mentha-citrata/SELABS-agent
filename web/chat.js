const messagesEl = document.getElementById('messages');
const inputEl = document.getElementById('input');
const sendBtn = document.getElementById('send');
const statusEl = document.getElementById('status');

function appendMessage(text, cls='assistant'){
  const d = document.createElement('div');
  d.className = `msg ${cls}`;
  d.textContent = text;
  messagesEl.appendChild(d);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function createSession(){
  const r = await fetch('/api/agent/session', {method:'POST'});
  if(!r.ok) throw new Error('创建 session 失败');
  const j = await r.json();
  return j.session_id;
}

async function sendMessage(sessionId, message){
  await fetch('/api/agent/send', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({session_id: sessionId, message})
  });
}

async function startChatFlow(userMessage){
  statusEl.textContent = '创建会话...';
  const sessionId = await createSession();
  statusEl.textContent = '打开流...';

  appendMessage(userMessage, 'user');

  // Start SSE
  const es = new EventSource(`/api/agent/stream?session_id=${sessionId}`);

  let partial = '';
  es.onmessage = (e)=>{
    try{
      const obj = JSON.parse(e.data);
      partial += obj.data;
      // render partial as assistant last message
      const last = messagesEl.querySelector('.assistant:last-child');
      if(last){ last.textContent = partial; }
      else { appendMessage(partial, 'assistant'); }
    }catch(err){ console.warn('invalid data', e.data); }
  };

  es.addEventListener('done', ()=>{
    statusEl.textContent = '完成';
    es.close();
  });

  es.onerror = (err)=>{
    statusEl.textContent = '流错误或已断开';
    es.close();
  };

  // Send message to trigger agent processing
  await sendMessage(sessionId, userMessage);
  statusEl.textContent = '等待回复...';
}

sendBtn.addEventListener('click', ()=>{
  const v = inputEl.value.trim();
  if(!v) return;
  inputEl.value = '';
  startChatFlow(v).catch(err=>{statusEl.textContent='错误: '+err.message;appendMessage('Error: '+err.message,'assistant')});
});

inputEl.addEventListener('keydown',(e)=>{ if(e.key==='Enter'){ sendBtn.click(); } });
