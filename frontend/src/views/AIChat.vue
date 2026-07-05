<template>
  <div class="ai-page">
    <!-- 左侧快捷面板 -->
    <aside class="ai-sidebar">
      <div class="sb-head">
        <span class="sb-mascot">🤗</span>
        <div>
          <span class="sb-title">AI 助手</span>
          <span class="sb-sub">招聘数据分析</span>
        </div>
      </div>

      <div class="sb-section">
        <span class="sb-label">✦ 快捷提问</span>
        <button v-for="q in quickQ" :key="q" @click="input=q;sendMessage()" class="q-btn">
          {{ q }}
        </button>
      </div>

      <div class="sb-footer">
        <div class="src-badge" :class="lastSrc">
          <span class="src-dot"></span>
          {{ lastSrc==='keyword'?'数据引擎':'AI 深度思考' }}
        </div>
        <div class="sb-deco-line">
          <span>❀</span><span>✦</span><span>❀</span>
        </div>
      </div>
    </aside>

    <!-- 主聊天区域 -->
    <div class="chat-main">
      <!-- 装饰云朵 -->
      <div class="cloud-deco c1">☁</div>
      <div class="cloud-deco c2">☁</div>

      <div class="chat-msgs" ref="msgRef">
        <div v-for="(msg,i) in messages" :key="i" :class="['msg-row', msg.role]">
          <div v-if="msg.role==='ai'" class="avatar ai-av">🤗</div>
          <div class="bubble-wrap">
            <div class="msg-bubble" v-html="renderMsg(msg.content)"></div>
            <span class="msg-time">{{ msg.time }}</span>
          </div>
          <div v-if="msg.role==='user'" class="avatar user-av">👀</div>
        </div>
        <div v-if="loading" class="msg-row ai">
          <div class="avatar ai-av">🤗</div>
          <div class="typing-bubble">
            <span class="ty-dot"></span><span class="ty-dot"></span><span class="ty-dot"></span>
          </div>
        </div>
      </div>

      <div class="input-area">
        <div class="input-wrap">
          <input
            v-model="input" :disabled="loading"
            placeholder="问我任何关于招聘数据的问题吧~"
            @keyup.enter="sendMessage"
          />
          <button @click="sendMessage" :disabled="loading||!input.trim()" class="send-btn">
            <span v-if="!loading">➤</span>
            <span v-else class="sending">✦</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref,nextTick } from 'vue'
import axios from 'axios'

const messages = ref([{
  role:'ai',
  content: '🌟 你好呀！我是招聘数据分析 AI 助手~\n\n可以问我这些问题哦：\n\n📌 "广州薪资最高的岗位是什么？"\n📌 "热门技能有哪些？"\n📌 "薪资分布情况如何？"\n📌 "哪些城市岗位最多？"\n\n快试试看吧 🤗',
  time: '刚刚',
}])
const input=ref(''), loading=ref(false), msgRef=ref(null), lastSrc=ref('')
const conversationId=ref(null)

const quickQ = [
  '广州薪资最高的岗位是什么？',
  '热门技能有哪些？',
  '薪资分布情况如何？',
  '哪些城市岗位最多？',
  '学历对薪资有什么影响？',
  '需要什么经验能找到工作？',
]

function renderMsg(text) {
  return text
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/\n/g,'<br>')
}

async function sendMessage() {
  if(!input.value.trim()||loading.value) return
  const msg=input.value
  messages.value.push({ role:'user',content:msg,time:'刚刚' })
  input.value=''; loading.value=true

  try {
    const body={ message:msg }
    if(conversationId.value) body.conversation_id=conversationId.value
    const {data}=await axios.post('/api/ai/chat',body)
    messages.value.push({ role:'ai',content:data.reply,time:'刚刚' })
    lastSrc.value=data.source||''
    if(data.conversation_id) conversationId.value=data.conversation_id
  } catch(e){
    messages.value.push({ role:'ai',content:'😢 抱歉，暂时无法回答，请稍后重试~' })
  } finally{
    loading.value=false
    await nextTick()
    msgRef.value.scrollTop=msgRef.value.scrollHeight
  }
}
</script>

<style scoped>
.ai-page { display: flex; height: calc(100vh - 74px); gap: 16px; }

/* ── 侧边栏 ── */
.ai-sidebar {
  width: 240px; flex-shrink: 0;
  background: rgba(26,20,50,0.85); border: 1.5px solid rgba(255,255,255,0.08);
  border-radius: var(--r-xl); padding: 22px 18px;
  display: flex; flex-direction: column;
}
.sb-head { display: flex; align-items: center; gap: 10px; margin-bottom: 22px; }
.sb-mascot { font-size: 32px; animation: bounce 2s ease-in-out infinite; }
.sb-title { display: block; font-size: 15px; font-weight: 800; }
.sb-sub { display: block; font-size: 11px; color: var(--text2); margin-top: 1px; }
.sb-section { display: flex; flex-direction: column; gap: 7px; flex: 1; }
.sb-label { font-size: 10px; color: var(--text2); letter-spacing: 2px; text-transform: uppercase; margin-bottom: 4px; }
.q-btn {
  width: 100%; padding: 9px 14px; border-radius: 14px; font-size: 12px;
  text-align: left; cursor: pointer; transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1);
  background: rgba(255,255,255,0.03); color: var(--text2);
  border: 1px solid transparent;
}
.q-btn:hover {
  background: linear-gradient(135deg, rgba(255,105,180,0.1), rgba(102,204,255,0.08));
  color: var(--pink); border-color: rgba(255,105,180,0.2);
  transform: translateX(4px);
}
.sb-footer { margin-top: 16px; display: flex; flex-direction: column; gap: 10px; align-items: center; }
.src-badge {
  padding: 5px 16px; border-radius: var(--r-pill);
  font-size: 11px; font-weight: 600; display: flex; align-items: center; gap: 6px;
  background: rgba(255,255,255,0.04); color: var(--text2);
}
.src-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--text2); }
.src-badge.keyword { background: rgba(102,204,255,0.1); color: var(--blue); }
.src-badge.keyword .src-dot { background: var(--blue); box-shadow: 0 0 6px var(--blue-g); }
.src-badge.dify { background: rgba(199,125,255,0.1); color: var(--purple); }
.src-badge.dify .src-dot { background: var(--purple); box-shadow: 0 0 6px var(--purple-g); }
.sb-deco-line { display: flex; gap: 12px; color: var(--pink); opacity: 0.4; font-size: 10px; }

/* ── 聊天主体 ── */
.chat-main {
  flex: 1; display: flex; flex-direction: column;
  background: rgba(26,20,50,0.85); border: 1.5px solid rgba(255,255,255,0.08);
  border-radius: var(--r-xl); overflow: hidden; position: relative;
}
.cloud-deco {
  position: absolute; pointer-events: none; z-index: 0;
  font-size: 60px; opacity: 0.04; color: #fff;
  animation: cloud-drift 25s linear infinite;
}
.cloud-deco.c1 { top: 8%; left: 5%; animation-delay: 0s; }
.cloud-deco.c2 { top: 15%; right: 8%; animation-delay: -12s; font-size: 45px; }
@keyframes cloud-drift {
  0% { transform: translateX(0); }
  50% { transform: translateX(40px); }
  100% { transform: translateX(0); }
}

.chat-msgs {
  flex: 1; overflow-y: auto; padding: 20px 24px; position: relative; z-index: 1;
}
.chat-msgs::-webkit-scrollbar { width: 4px; }
.chat-msgs::-webkit-scrollbar-thumb { background: rgba(255,105,180,0.2); border-radius: 4px; }

.msg-row { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 18px; }
.msg-row.user { flex-direction: row-reverse; }
.avatar {
  width: 38px; height: 38px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px;
}
.ai-av { background: linear-gradient(135deg, rgba(255,105,180,0.2), rgba(199,125,255,0.2)); }
.user-av { background: linear-gradient(135deg, rgba(102,204,255,0.2), rgba(127,255,212,0.2)); }
.bubble-wrap { display: flex; flex-direction: column; gap: 4px; max-width: 72%; }
.msg-bubble {
  padding: 14px 20px; border-radius: 22px;
  font-size: 14px; line-height: 1.75; word-break: break-word;
}
.msg-row.ai .msg-bubble {
  background: rgba(255,255,255,0.04); color: var(--text);
  border: 1px solid rgba(255,255,255,0.06);
  border-top-left-radius: 8px;
}
.msg-row.user .msg-bubble {
  background: linear-gradient(135deg, var(--pink), #FF1493);
  color: #fff; border-top-right-radius: 8px;
  box-shadow: 0 4px 18px rgba(255,105,180,0.3);
}
.msg-time { font-size: 10px; color: var(--text2); padding: 0 8px; }
.msg-row.user .msg-time { text-align: right; }

/* 打字动画 */
.typing-bubble {
  display: flex; align-items: center; gap: 7px;
  padding: 16px 24px; border-radius: 22px;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);
  border-top-left-radius: 8px;
}
.ty-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--pink);
  animation: ty-bounce 1.4s infinite both;
}
.ty-dot:nth-child(2) { animation-delay: 0.2s; background: var(--purple); }
.ty-dot:nth-child(3) { animation-delay: 0.4s; background: var(--blue); }
@keyframes ty-bounce {
  0%,80%,100% { transform: scale(0.4); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
}

/* ── 输入区 ── */
.input-area { padding: 14px 22px; border-top: 1.5px solid rgba(255,255,255,0.06); position: relative; z-index: 1; }
.input-wrap {
  display: flex; align-items: center; gap: 10px;
  background: rgba(255,255,255,0.03);
  border: 1.5px solid rgba(255,255,255,0.06);
  border-radius: var(--r-pill); padding: 4px 4px 4px 22px;
  transition: all 0.35s;
}
.input-wrap:focus-within {
  border-color: var(--purple);
  box-shadow: 0 0 24px var(--purple-g);
}
.input-wrap input {
  flex: 1; padding: 10px 0; border: none; background: transparent;
  color: var(--text); font-size: 14px; outline: none;
}
.input-wrap input::placeholder { color: var(--text2); }
.send-btn {
  width: 44px; height: 44px; border-radius: 50%; border: none;
  background: linear-gradient(135deg, var(--pink), var(--purple));
  color: #fff; font-size: 18px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1);
  box-shadow: 0 4px 18px var(--pink-g);
}
.send-btn:hover:not(:disabled) {
  transform: scale(1.1);
  box-shadow: 0 6px 26px rgba(255,105,180,0.6);
}
.send-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.sending { animation: spin 1s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes bounce {
  0%,100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}
</style>
