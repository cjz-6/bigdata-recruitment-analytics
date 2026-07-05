<template>
  <div class="jobs-page">
    <!-- 搜索栏 — 大圆角气泡 -->
    <div class="search-bar">
      <div class="srch-wrap" ref="searchWrap">
        <span class="srch-ico">🔍</span>
        <input v-model="keyword" placeholder="搜岗位 / 公司..." @keyup.enter="fetchJobs" @input="onKeywordInput" @focus="showSuggestions=true" @blur="onBlur" />
        <span v-if="keyword" class="clear-btn" @click="keyword='';fetchJobs();suggestions={titles:[],companies:[]}">✕</span>
        <!-- 联想下拉 -->
        <div v-if="showSuggestions && (suggestions.titles.length||suggestions.companies.length)" class="suggest-drop">
          <template v-if="suggestions.titles.length">
            <div class="suggest-head">💼 岗位</div>
            <div v-for="t in suggestions.titles" :key="'t'+t.name" class="suggest-item" @mousedown.prevent="pickSuggest(t.name)">
              {{ t.name }}<span class="suggest-cnt">{{ t.count }}</span>
            </div>
          </template>
          <template v-if="suggestions.companies.length">
            <div class="suggest-head">🏢 公司</div>
            <div v-for="c in suggestions.companies" :key="'c'+c.name" class="suggest-item" @mousedown.prevent="pickSuggest(c.name)">
              {{ c.name }}<span class="suggest-cnt">{{ c.count }}</span>
            </div>
          </template>
        </div>
      </div>
      <select v-model="selectedCity" class="city-sel">
        <option value="">🌐 全部城市</option>
        <option v-for="c in cities" :key="c.city" :value="c.city">{{ c.city }} ({{ c.count }})</option>
      </select>
      <select v-model="selectedEdu" class="city-sel">
        <option value="">🏫 全部学历</option>
        <option v-for="e in eduOptions" :key="e" :value="e">{{ e }}</option>
      </select>
      <button @click="fetchJobs" class="search-btn">
        <span class="btn-spark">✦</span> 搜索
      </button>
    </div>

    <!-- 统计条 -->
    <div class="stat-bar">
      <span class="stat-chip">📊 共 <strong>{{ total }}</strong> 个岗位</span>
      <span class="stat-chip">📍 {{ cities.length }} 个城市</span>
      <span class="stat-chip">📄 第 <strong>{{ page }}</strong>/<strong>{{ totalPages }}</strong> 页</span>
    </div>

    <!-- 岗位表格 -->
    <div class="table-bubble">
      <table class="jobs-table">
        <thead>
          <tr>
            <th>💼 岗位名称</th><th>🏢 公司</th><th>📍 城市</th>
            <th>💰 薪资</th><th>🎓 经验</th><th>🏫 学历</th><th>🛠 技能</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(job,i) in jobs" :key="job.id" :style="{animationDelay: i*0.03+'s'}" class="job-row">
            <td class="col-title">{{ job.job_title }}</td>
            <td class="col-company">{{ job.company }}</td>
            <td><span class="city-chip">{{ job.city }}</span></td>
            <td class="col-salary">{{ job.salary_raw || '面议' }}</td>
            <td>{{ job.experience || '-' }}</td>
            <td>{{ job.education || '-' }}</td>
            <td class="skills-cell">
              <template v-if="parseSkills(job.skills).length">
                <span class="skill-chip" v-for="sk in parseSkills(job.skills).slice(0,8)" :key="sk">{{ sk }}</span>
                <span v-if="parseSkills(job.skills).length>8" class="skill-more">+{{ parseSkills(job.skills).length-8 }}</span>
              </template>
              <span v-else class="no-skill">· · ·</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="pagination">
      <button :disabled="page<=1" @click="page--;fetchJobs()" class="page-btn">◀ 上一页</button>
      <div class="page-dots">
        <span v-for="p in displayPages" :key="p"
              :class="['page-dot',{active:p===page}]"
              @click="page=p;fetchJobs()">{{ p }}</span>
      </div>
      <button :disabled="page>=totalPages" @click="page++;fetchJobs()" class="page-btn">下一页 ▶</button>
    </div>
  </div>
</template>

<script setup>
import { ref,onMounted,computed } from 'vue'
import axios from 'axios'

const jobs=ref([]), cities=ref([]), keyword=ref(''), selectedCity=ref(''), selectedEdu=ref(''), page=ref(1), total=ref(0)
const suggestions=ref({titles:[],companies:[]})
const showSuggestions=ref(false)
let suggestTimer=null

const perPage=12
const eduOptions=['初中及以下','高中','中技/中专','大专','本科','硕士','博士']

const totalPages=computed(()=>Math.ceil(total.value/perPage)||1)
const displayPages=computed(()=>{
  const p=[],start=Math.max(1,page.value-2),end=Math.min(totalPages.value,page.value+2)
  for(let i=start;i<=end;i++) p.push(i)
  return p
})

function parseSkills(skills){
  if(!skills||skills==='null') return []
  try{ return JSON.parse(skills) } catch{ return skills.split(/[,，]/).map(s=>s.trim()).filter(Boolean) }
}

async function fetchJobs(){
  const params={ page:page.value, per_page:perPage }
  if(keyword.value) params.keyword=keyword.value
  if(selectedCity.value) params.city=selectedCity.value
  if(selectedEdu.value) params.education=selectedEdu.value
  const {data}=await axios.get('/api/jobs/',{params})
  jobs.value=data.items; total.value=data.total
}
async function fetchCities(){
  const {data}=await axios.get('/api/jobs/cities')
  cities.value=data
}

function onKeywordInput(){
  clearTimeout(suggestTimer)
  const q = keyword.value?.trim()
  if(q && q.length>=2){
    suggestTimer=setTimeout(async()=>{
      try{
        const {data}=await axios.get('/api/jobs/autocomplete',{params:{q}})
        suggestions.value=data; showSuggestions.value=true
      }catch{ suggestions.value={titles:[],companies:[]} }
    },200)
  } else {
    suggestions.value={titles:[],companies:[]}
  }
}

function pickSuggest(name){
  keyword.value=name; showSuggestions.value=false; page.value=1; fetchJobs()
}

function onBlur(){
  setTimeout(()=>{showSuggestions.value=false},150)
}

onMounted(()=>{fetchJobs();fetchCities()})
</script>

<style scoped>
.jobs-page {
  height: calc(100vh - 74px);
  display: flex; flex-direction: column;
  padding: 4px; gap: 12px;
}

/* ── 搜索栏 ── */
.search-bar { flex-shrink: 0; display: flex; gap: 12px; }
.srch-wrap {
  flex: 1; display: flex; align-items: center; gap: 10px;
  background: rgba(26,20,50,0.85); border: 1.5px solid rgba(255,105,180,0.2);
  border-radius: var(--r-pill); padding: 0 20px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.srch-wrap:focus-within {
  border-color: var(--pink);
  box-shadow: 0 0 28px var(--pink-g);
}
.srch-ico { font-size: 16px; opacity: 0.7; }
.srch-wrap input {
  flex: 1; padding: 11px 0; border: none; background: transparent;
  color: var(--text); font-size: 14px; outline: none;
}
.srch-wrap input::placeholder { color: var(--text2); }
.clear-btn {
  cursor: pointer; color: var(--text2); font-size: 14px;
  transition: color 0.2s;
}
.clear-btn:hover { color: var(--pink); }
.city-sel {
  padding: 9px 16px; border-radius: var(--r-pill);
  border: 1.5px solid rgba(102,204,255,0.2); background: rgba(26,20,50,0.85);
  color: var(--text); font-size: 13px; cursor: pointer;
  min-width: 160px; outline: none;
}
.city-sel:focus { border-color: var(--blue); box-shadow: 0 0 22px var(--blue-g); }
.search-btn {
  padding: 9px 26px; border: none; border-radius: var(--r-pill);
  background: linear-gradient(135deg, var(--pink), #FF1493);
  color: #fff; font-size: 14px; font-weight: 700; cursor: pointer;
  display: flex; align-items: center; gap: 6px;
  transition: all 0.35s cubic-bezier(0.34,1.56,0.64,1);
  box-shadow: 0 4px 20px rgba(255,105,180,0.35);
}
.search-btn:hover {
  transform: scale(1.06);
  box-shadow: 0 6px 28px rgba(255,105,180,0.55);
}
.btn-spark { font-size: 16px; animation: pop 1.8s ease-in-out infinite; }

/* ── 统计条 ── */
.stat-bar { flex-shrink: 0; display: flex; gap: 10px; }
.stat-chip {
  padding: 4px 14px; border-radius: var(--r-pill);
  font-size: 11px; background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06); color: var(--text2);
}
.stat-chip strong { color: var(--text); }

/* ── 表格气泡（内部滚动） ── */
.table-bubble {
  flex: 1; min-height: 0;
  overflow-y: auto; overflow-x: hidden;
  background: rgba(26,20,50,0.85); border: 1.5px solid rgba(255,255,255,0.08);
  border-radius: var(--r-xl);
}
.table-bubble::-webkit-scrollbar { width: 5px; }
.table-bubble::-webkit-scrollbar-thumb { background: rgba(255,105,180,0.2); border-radius: 4px; }
.jobs-table { width: 100%; border-collapse: collapse; }
.jobs-table thead {
  position: sticky; top: 0; z-index: 2;
}
.jobs-table th {
  padding: 13px 16px; text-align: left; font-size: 11px; font-weight: 700;
  color: var(--text2); letter-spacing: 1px; text-transform: uppercase;
  border-bottom: 1.5px solid rgba(255,255,255,0.06);
  background: rgba(26,20,50,0.95);
}
.jobs-table td { padding: 11px 16px; font-size: 13px; border-bottom: 1px solid rgba(255,255,255,0.03); }
.job-row {
  animation: fade-up 0.4s ease-out both;
  transition: background 0.25s;
}
.job-row:hover { background: rgba(255,105,180,0.05); }
.jobs-table tbody tr:last-child td { border-bottom: none; }
.col-title { font-weight: 600; color: var(--text); }
.col-company { color: var(--text2); }
.col-salary { color: var(--pink); font-weight: 700; }
.city-chip {
  display: inline-block; padding: 2px 12px; border-radius: var(--r-pill);
  font-size: 11px; font-weight: 600;
  background: rgba(102,204,255,0.1); color: var(--blue);
  border: 1px solid rgba(102,204,255,0.2);
}

/* ── 技能标签 ── */
.skills-cell { display: flex; flex-wrap: wrap; gap: 4px; max-width: 280px; }
.skill-chip {
  display: inline-block; padding: 3px 10px; border-radius: var(--r-pill);
  font-size: 10px; font-weight: 600;
  background: linear-gradient(135deg, rgba(199,125,255,0.15), rgba(255,105,180,0.1));
  color: var(--purple); border: 1px solid rgba(199,125,255,0.25);
  transition: all 0.25s; white-space: nowrap;
}
.skill-chip:hover { transform: translateY(-2px) scale(1.08); border-color: var(--purple); }
.skill-more {
  padding: 3px 8px; border-radius: var(--r-pill);
  font-size: 10px; color: var(--text2); background: rgba(255,255,255,0.03);
}
.no-skill { color: var(--text2); font-size: 11px; letter-spacing: 2px; }

/* ── 分页 ── */
.pagination {
  flex-shrink: 0;
  display: flex; justify-content: center; align-items: center; gap: 12px;
}
.page-btn {
  padding: 8px 20px; border-radius: var(--r-pill);
  font-size: 12px; font-weight: 600; cursor: pointer;
  background: var(--card); color: var(--text);
  border: 1.5px solid rgba(255,255,255,0.08);
  transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1);
}
.page-btn:hover:not(:disabled) {
  border-color: var(--blue); box-shadow: 0 0 18px var(--blue-g);
  transform: scale(1.06);
}
.page-btn:disabled { opacity: 0.25; cursor: not-allowed; }
.page-dots { display: flex; gap: 6px; }
.page-dot {
  width: 34px; height: 34px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; cursor: pointer;
  background: rgba(255,255,255,0.03); color: var(--text2);
  transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1);
}
.page-dot:hover { background: rgba(255,105,180,0.12); color: var(--pink); }
.page-dot.active {
  background: linear-gradient(135deg, var(--pink), var(--purple));
  color: #fff; box-shadow: 0 0 18px var(--pink-g);
}

@keyframes fade-up {
  from { opacity:0; transform:translateY(10px); }
  to { opacity:1; transform:translateY(0); }
}
/* ── 联想下拉 ── */
.suggest-drop {
  position: absolute; top: calc(100% + 8px); left: 0; right: 0;
  background: rgba(20,14,44,0.98); border: 1.5px solid rgba(255,105,180,0.2);
  border-radius: 16px; padding: 8px; z-index: 100;
  box-shadow: 0 12px 40px rgba(0,0,0,0.6);
  max-height: 320px; overflow-y: auto;
}
.suggest-head { padding: 6px 10px 4px; font-size: 11px; color: var(--text2); opacity: 0.7; }
.suggest-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 14px; border-radius: 10px; cursor: pointer;
  font-size: 13px; color: var(--text); transition: background 0.15s;
}
.suggest-item:hover { background: rgba(255,105,180,0.1); }
.suggest-cnt {
  font-size: 10px; color: var(--text2); background: rgba(255,255,255,0.05);
  padding: 2px 8px; border-radius: 8px;
}
.srch-wrap { position: relative; }

@keyframes pop {
  0%,100% { transform:scale(1); }
  50% { transform:scale(1.15); }
}
</style>
