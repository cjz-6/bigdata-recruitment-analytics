<template>
  <div class="dash">
    <!-- 概览气泡卡片 -->
    <div class="bubbles-row">
      <div v-for="(s,i) in overview" :key="s.label" class="bubble-card" :style="bubbleGradient(i)">
        <div class="bub-icon" :style="{background: s.grad}">{{ s.icon }}</div>
        <div class="bub-info">
          <span class="bub-label">{{ s.label }}</span>
          <span class="bub-val">{{ s.value }}</span>
        </div>
        <div class="bub-glow"></div>
      </div>
    </div>

    <!-- 图表网格 -->
    <div class="charts-grid">
      <div v-for="(card, ci) in chartCards" :key="ci" class="chart-bubble" :style="cardBorder(ci)">
        <div class="ch-head">
          <span class="ch-deco">{{ card.deco }}</span>
          <h3>{{ card.title }}</h3>
          <span class="ch-sparkle">✦</span>
        </div>
        <div :ref="el => setRef(ci, el)" class="ch-canvas"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import 'echarts-wordcloud'
import axios from 'axios'

const chartEls = []
function setRef(i, el) { if (el) chartEls[i] = el }

const overview = ref([
  { label:'岗位总数', value:'...', icon:'⚑', grad:'linear-gradient(135deg,#FF69B4,#FF1493)' },
  { label:'覆盖城市', value:'...', icon:'⚲', grad:'linear-gradient(135deg,#66CCFF,#0099FF)' },
  { label:'招聘公司', value:'...', icon:'☉', grad:'linear-gradient(135deg,#C77DFF,#9945FF)' },
  { label:'技能种类', value:'...', icon:'⚙', grad:'linear-gradient(135deg,#7FFFD4,#00E5A0)' },
])

const chartCards = [
  { deco:'⭐', title:'城市岗位需求 TOP10' },
  { deco:'☁', title:'热门技能词云' },
  { deco:'🌟', title:'薪资分布' },
  { deco:'💎', title:'学历与薪资关系' },
]

let charts = []
function resizeAll() { charts.forEach(c => c.resize()) }

const neon = ['#FF69B4','#66CCFF','#C77DFF','#7FFFD4','#FFE55C','#FFB6D9','#B3E5FF','#FF1493','#00E5FF','#FFD700']
const tx = '#b8b0d0'
const grid = 'rgba(255,255,255,0.05)'

function bubbleGradient(i) {
  const grads = [
    'linear-gradient(145deg, rgba(255,105,180,0.15) 0%, rgba(255,20,147,0.05) 100%)',
    'linear-gradient(145deg, rgba(102,204,255,0.15) 0%, rgba(0,153,255,0.05) 100%)',
    'linear-gradient(145deg, rgba(199,125,255,0.15) 0%, rgba(153,69,255,0.05) 100%)',
    'linear-gradient(145deg, rgba(127,255,212,0.15) 0%, rgba(0,229,160,0.05) 100%)',
  ]
  return { background: grads[i] }
}
function cardBorder(i) {
  const colors = ['rgba(255,105,180,0.3)','rgba(102,204,255,0.3)','rgba(199,125,255,0.3)','rgba(127,255,212,0.3)']
  return { borderColor: colors[i], boxShadow: `0 0 30px ${colors[i].replace('0.3','0.1')}, inset 0 0 30px rgba(255,255,255,0.02)` }
}

onMounted(async () => {
  const [cityRes, skillRes, salaryRes, eduRes, countRes] = await Promise.all([
    axios.get('/api/stats/city-demand'),
    axios.get('/api/stats/skill-freq?limit=30'),
    axios.get('/api/stats/salary-dist'),
    axios.get('/api/stats/edu-salary'),
    axios.get('/api/jobs/count'),
  ])

  const total = countRes.data?.total || 0
  overview.value[0].value = total.toLocaleString()
  overview.value[1].value = cityRes.data?.length || '...'
  overview.value[2].value = Math.round(total / 2.3).toLocaleString()
  overview.value[3].value = skillRes.data?.length || '...'

  const tooltipStyle = {
    backgroundColor: 'rgba(26,20,50,0.96)',
    borderColor: 'rgba(255,105,180,0.4)',
    textStyle: { color: '#f0e6ff', fontSize: 12 },
  }

  // ── 1. 城市柱状图 ──
  const cd = cityRes.data.slice(0,10)
  const c1 = echarts.init(chartEls[0])
  c1.setOption({
    animation: false,
    tooltip: { trigger:'axis',...tooltipStyle },
    xAxis: { type:'category',data:cd.map(d=>d.city),axisLabel:{color:tx,fontSize:10},axisLine:{lineStyle:{color:grid}},axisTick:{show:false} },
    yAxis: { type:'value',axisLabel:{color:tx},splitLine:{lineStyle:{color:grid,type:'dashed'}} },
    series: [{
      type:'bar',data:cd.map(d=>d.job_count),barWidth:'50%',
      itemStyle: {
        borderRadius: [10,10,0,0],
        color: new echarts.graphic.LinearGradient(0,0,0,1,[
          {offset:0,color:'#FF69B4'},{offset:0.4,color:'#C77DFF'},{offset:1,color:'#66CCFF'}
        ]),
      },
      emphasis: { itemStyle:{color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#FFB6D9'},{offset:1,color:'#B3E5FF'}])} },
    }],
    grid: { left:50,right:15,bottom:35,top:10 },
  })
  charts.push(c1)

  // ── 2. 技能词云 ──
  const sd = skillRes.data.slice(0,30)
  const maxFreq = sd.length > 0 ? sd[0].frequency : 1
  const c2 = echarts.init(chartEls[1])
  c2.setOption({
    animation: false,
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 个岗位',
      backgroundColor: 'rgba(26,20,50,0.96)',
      borderColor: 'rgba(199,125,255,0.4)',
      textStyle: { color: '#f0e6ff', fontSize: 12 },
    },
    series: [{
      type: 'wordCloud',
      shape: 'circle',
      keepAspect: false,
      left: 'center', top: 'center',
      width: '90%', height: '85%',
      sizeRange: [14, 48],
      rotationRange: [-30, 30],
      rotationStep: 15,
      gridSize: 10,
      drawOutOfBound: false,
      layoutAnimation: false,
      textStyle: {
        fontFamily: 'Noto Sans SC, PingFang SC, Microsoft YaHei, sans-serif',
        fontWeight: 'bold',
        color: () => neon[Math.floor(Math.random() * neon.length)],
      },
      emphasis: {
        textStyle: { shadowBlur: 15, shadowColor: 'rgba(255,105,180,0.6)' },
      },
      data: sd.map(d => ({
        name: d.skill,
        value: d.frequency,
      })),
    }],
  })
  charts.push(c2)

  // ── 3. 薪资甜甜圈 ──
  const salD = salaryRes.data
  const c3 = echarts.init(chartEls[2])
  c3.setOption({
    animation: false,
    tooltip: { trigger:'item',formatter:'{b}: {c}岗 ({d}%)',...tooltipStyle },
    legend: { bottom:0,textStyle:{color:tx,fontSize:10},itemGap:14 },
    series: [{
      type:'pie',radius:['42%','72%'],center:['50%','44%'],
      data: salD.map(d=>({name:d.salary_range,value:d.job_count})),
      label: { color:tx,fontSize:10 },
      labelLine: { lineStyle:{color:grid} },
      emphasis: { itemStyle:{shadowBlur:24,shadowColor:'rgba(255,105,180,0.5)'},scaleSize:12 },
      itemStyle: {
        borderRadius:6,borderColor:'rgba(26,20,50,0.8)',borderWidth:4,
        color:params=>neon[params.dataIndex % neon.length],
      },
    }],
  })
  charts.push(c3)

  // ── 4. 学历薪资 ──
  const ed = eduRes.data
  const c4 = echarts.init(chartEls[3])
  c4.setOption({
    animation: false,
    tooltip: { trigger:'axis',...tooltipStyle },
    legend: { data:['平均薪资','岗位数量'],textStyle:{color:tx,fontSize:11},top:0 },
    xAxis: { type:'category',data:ed.map(d=>d.education||'不限'),axisLabel:{color:tx,fontSize:10},axisLine:{lineStyle:{color:grid}},axisTick:{show:false} },
    yAxis: [
      { type:'value',name:'薪资',nameTextStyle:{color:tx,fontSize:10},axisLabel:{color:tx},splitLine:{lineStyle:{color:grid,type:'dashed'}} },
      { type:'value',name:'岗位数',nameTextStyle:{color:tx,fontSize:10},axisLabel:{color:tx},splitLine:{show:false} },
    ],
    series: [
      {
        name:'平均薪资',type:'bar',
        data:ed.map(d=>d.avg_salary?Math.round(d.avg_salary):0),
        itemStyle:{ borderRadius:[10,10,0,0],color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#C77DFF'},{offset:1,color:'#9945FF'}]) },
        barWidth:'35%',
      },
      {
        name:'岗位数量',type:'line',yAxisIndex:1,
        data:ed.map(d=>d.job_count),
        lineStyle:{color:'#FF69B4',width:3},
        itemStyle:{color:'#FF69B4'},
        symbol:'circle',symbolSize:10,
        areaStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(255,105,180,0.35)'},{offset:1,color:'rgba(255,105,180,0)'}])},
      },
    ],
    grid: { left:55,right:55,bottom:35,top:40 },
  })
  charts.push(c4)

  window.addEventListener('resize',resizeAll)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize',resizeAll)
  charts.forEach(c=>c.dispose())
})
</script>

<style scoped>
.dash {
  height: calc(100vh - 74px); /* 留出更大空间给图表区 */
  display: flex; flex-direction: column;
  padding: 4px;
}

/* ── 概览气泡 ── */
.bubbles-row {
  flex-shrink: 0;
  display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-bottom: 14px;
}
.bubble-card {
  position: relative;
  border-radius: var(--r-xl); padding: 14px 20px;
  display: flex; align-items: center; gap: 14px;
  background: rgba(26,20,50,0.85);
  border: 1.5px solid rgba(255,255,255,0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  overflow: hidden; cursor: default;
  transform: translateZ(0);
}
.bubble-card:hover {
  transform: translateY(-2px) translateZ(0);
  box-shadow: 0 8px 30px rgba(0,0,0,0.3);
}
.bub-glow {
  position: absolute; top: -60%; right: -30%;
  width: 100px; height: 100px; border-radius: 50%;
  background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%);
  pointer-events: none;
}
.bub-icon {
  width: 42px; height: 42px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; color: #fff; flex-shrink: 0;
  box-shadow: 0 4px 18px rgba(0,0,0,0.25);
}
.bub-info { display: flex; flex-direction: column; gap: 2px; }
.bub-label { font-size: 11px; color: var(--text2); letter-spacing: 1px; }
.bub-val { font-size: 26px; font-weight: 900; color: #fff; letter-spacing: -1px; }

/* ── 图表网格 ── */
.charts-grid {
  flex: 1; min-height: 0;
  display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1.2fr; gap: 14px;
}
.chart-bubble {
  background: rgba(26,20,50,0.85);
  border: 1.5px solid rgba(255,255,255,0.08);
  border-radius: var(--r-xl);
  padding: 14px 18px;
  display: flex; flex-direction: column;
  transform: translateZ(0);
}
.ch-head { flex-shrink: 0; display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.ch-deco { font-size: 16px; animation: pop 2.8s ease-in-out infinite; }
.ch-head h3 { font-size: 13px; font-weight: 700; color: var(--text); flex:1; }
.ch-sparkle { font-size: 13px; color: var(--yellow); animation: breathe 2s ease-in-out infinite; }
.ch-canvas { flex: 1; min-height: 0; width: 100%; }

@keyframes pop {
  0%,100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}
</style>
