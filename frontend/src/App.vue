<template>
  <div id="app">
    <!-- 动态粒子背景 -->
    <div class="parallax-bg">
      <span v-for="i in 12" :key="'p'+i" class="par-p" :style="parStyle(i)"></span>
      <span v-for="i in 6" :key="'s'+i" class="par-star" :style="starStyle(i)">★</span>
    </div>

    <!-- 自定义光标 — 猫爪 -->
    <div ref="pawRef" class="cat-paw">
      <div class="paw-inner">
        <span class="paw-pad"></span>
        <span class="paw-bean b1"></span>
        <span class="paw-bean b2"></span>
        <span class="paw-bean b3"></span>
        <span class="paw-bean b4"></span>
      </div>
    </div>

    <!-- 樱花拖尾容器 -->
    <div ref="trailRef" class="trail-layer"></div>

    <nav class="navbar">
      <div class="nav-brand">
        <span class="brand-deco">❀✦❀</span>
        <h1>招聘数据智能分析</h1>
      </div>
      <div class="nav-links">
        <router-link to="/">
          <span class="nav-dot"></span>☷ 数据大屏
        </router-link>
        <router-link to="/jobs">
          <span class="nav-dot"></span>☰ 岗位列表
        </router-link>
        <router-link to="/ai">
          <span class="nav-dot"></span>❀ AI 问答
        </router-link>
      </div>
    </nav>
    <main>
      <router-view v-slot="{ Component }">
        <transition name="page-bounce" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const pawRef = ref(null)
const trailRef = ref(null)

// ── 光标状态（B方案：直接跟手）──
let mouseX = -999, mouseY = -999
let wasOutside = true
// 拖尾独立弹性坐标（保留果冻感作为视觉装饰）
let trailX = -999, trailY = -999
const TRAIL_LERP = 0.12 // 拖尾弹性系数，越小越黏

// ── 拖尾花瓣池 ──
const TRAIL_COUNT = 25
const petals = []
let petalIdx = 0
let lastTrailX = -999, lastTrailY = -999
const TRAIL_SPACING = 28 // 每移动多少像素生成一片花瓣

function createPetalPool() {
  const container = trailRef.value
  if (!container) return
  for (let i = 0; i < TRAIL_COUNT; i++) {
    const el = document.createElement('span')
    el.className = 'sakura'
    el.style.cssText = 'position:fixed;pointer-events:none;z-index:99998;opacity:0;'
    container.appendChild(el)
    petals.push({ el, active: false, timer: null })
  }
}

function spawnPetal(x, y) {
  const petal = petals[petalIdx]
  // 清除上一个定时器
  if (petal.timer) clearTimeout(petal.timer)

  const size = 5 + Math.random() * 8
  const driftX = (Math.random() - 0.5) * 40
  const driftY = -20 - Math.random() * 30
  const rot = Math.random() * 360
  const hue = 330 + Math.random() * 25 // 粉色系

  petal.el.style.cssText = `
    position:fixed;pointer-events:none;z-index:99998;
    left:${x}px;top:${y}px;
    width:${size}px;height:${size * 1.2}px;
    background:radial-gradient(ellipse at center,hsl(${hue},90%,80%),hsl(${hue},80%,65%));
    border-radius:50% 0 50% 0;
    opacity:0.9;
    transform:translate(-50%,-50%) rotate(${rot}deg);
    transition:all 0.9s cubic-bezier(0.25,0.46,0.45,0.94);
  `

  // 触发动画（下一帧改变属性，让 transition 生效）
  requestAnimationFrame(() => {
    petal.el.style.opacity = '0'
    petal.el.style.transform = `translate(${-50 + driftX}%,${-50 + driftY}%) rotate(${rot + 60}deg) scale(0.2)`
  })

  petal.timer = setTimeout(() => { petal.el.style.opacity = '0' }, 950)
  petalIdx = (petalIdx + 1) % TRAIL_COUNT
}

// ── 动画循环 ──
let animId = null
function animate() {
  if (mouseX < 0) {
    // 鼠标已离开窗口 — 立即隐藏
    if (pawRef.value) pawRef.value.style.opacity = '0'
    wasOutside = true
  } else {
    // 刚回到窗口 — 瞬间定位
    if (wasOutside) {
      trailX = mouseX; trailY = mouseY
      if (pawRef.value) pawRef.value.style.opacity = '1'
      wasOutside = false
    }

    // 猫爪：直接贴到鼠标位置（零延迟）
    if (pawRef.value) {
      pawRef.value.style.left = mouseX + 'px'
      pawRef.value.style.top = mouseY + 'px'
    }

    // 拖尾：弹性跟随（保留果冻装饰效果）
    trailX += (mouseX - trailX) * TRAIL_LERP
    trailY += (mouseY - trailY) * TRAIL_LERP

    const tdx = trailX - lastTrailX
    const tdy = trailY - lastTrailY
    const tdist = Math.sqrt(tdx * tdx + tdy * tdy)
    if (tdist > TRAIL_SPACING) {
      spawnPetal(trailX, trailY)
      lastTrailX = trailX
      lastTrailY = trailY
    }
  }

  animId = requestAnimationFrame(animate)
}

// ── 鼠标事件 ──
function onMouseMove(e) {
  mouseX = e.clientX
  mouseY = e.clientY
}
function onMouseLeave() {
  mouseX = -1; mouseY = -1
}

// ── 输入框/可点击元素上切换光标形态 ──
function onPointerOver(e) {
  const tag = e.target.tagName
  const isInteractive = tag === 'INPUT' || tag === 'SELECT' ||
    tag === 'BUTTON' || tag === 'TEXTAREA' ||
    tag === 'A' || e.target.closest('a,button,input,select,textarea,[role="button"]')
  if (isInteractive && pawRef.value) {
    pawRef.value.classList.add('is-clickable')
  }
}
function onPointerOut(e) {
  if (pawRef.value) pawRef.value.classList.remove('is-clickable')
}

onMounted(() => {
  createPetalPool()
  // 初始隐藏猫爪，鼠标进入后才显示
  if (pawRef.value) pawRef.value.style.opacity = '0'
  document.addEventListener('mousemove', onMouseMove, { passive: true })
  document.addEventListener('mouseleave', onMouseLeave)
  document.addEventListener('pointerover', onPointerOver, { passive: true })
  document.addEventListener('pointerout', onPointerOut, { passive: true })
  animId = requestAnimationFrame(animate)
})

onBeforeUnmount(() => {
  cancelAnimationFrame(animId)
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseleave', onMouseLeave)
  document.removeEventListener('pointerover', onPointerOver)
  document.removeEventListener('pointerout', onPointerOut)
  // 清理花瓣定时器
  petals.forEach(p => { if (p.timer) clearTimeout(p.timer) })
})

// ── 背景粒子参数（沿用） ──
function parStyle(i) {
  const colors = ['#FF69B4','#66CCFF','#C77DFF','#7FFFD4','#FFE55C','#FFB6D9','#B3E5FF']
  return {
    left: ((i * 137 + 53) % 100) + '%',
    width: (4 + (i % 8)) + 'px',
    height: (4 + (i % 8)) + 'px',
    background: colors[i % colors.length],
    animationDuration: (8 + (i % 14)) + 's',
    animationDelay: (i * 0.7) + 's',
    borderRadius: i % 5 === 0 ? '50%' : i % 5 === 1 ? '3px' : '50%',
    boxShadow: `0 0 ${6 + i % 6}px ${colors[i % colors.length]}`,
  }
}
function starStyle(i) {
  return {
    left: ((i * 179 + 23) % 94) + '%',
    fontSize: (10 + (i % 16)) + 'px',
    color: ['#FFE55C','#FF69B4','#66CCFF','#C77DFF'][i % 4],
    animationDuration: (10 + (i % 12)) + 's',
    animationDelay: (i * 1.1) + 's',
    opacity: 0.3 + (i % 5) * 0.12,
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --bg: #1a1a2e;
  --bg2: #16213e;
  --card: rgba(26, 20, 50, 0.75);
  --card-border: rgba(255, 255, 255, 0.08);
  --text: #f0e6ff;
  --text2: #b8b0d0;
  --pink: #FF69B4;
  --pink-g: rgba(255,105,180,0.45);
  --blue: #66CCFF;
  --blue-g: rgba(102,204,255,0.45);
  --mint: #7FFFD4;
  --mint-g: rgba(127,255,212,0.4);
  --yellow: #FFE55C;
  --yellow-g: rgba(255,229,92,0.4);
  --purple: #C77DFF;
  --purple-g: rgba(199,125,255,0.45);
  --r-xl: 24px;
  --r-lg: 20px;
  --r-md: 16px;
  --r-pill: 50px;
}

/* ── 隐藏系统光标 ── */
html, body, div, canvas, svg, img, p, span, h1, h2, h3, h4, h5, h6,
table, thead, tbody, tr, th, td, section, article, header, footer,
nav, aside, main, button, input, select, textarea, a, label, option { cursor: none !important; }

body {
  font-family: 'Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif;
  background: var(--bg);
  background-image:
    radial-gradient(ellipse at 20% 20%, rgba(255,105,180,0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 80%, rgba(102,204,255,0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 50%, rgba(199,125,255,0.05) 0%, transparent 60%);
  color: var(--text);
  min-height: 100vh;
  overflow-x: hidden;
}

/* ── 猫爪光标 ── */
.cat-paw {
  position: fixed; left: 0; top: 0;
  pointer-events: none; z-index: 99999;
  width: 36px; height: 36px;
  transform: translate(-50%, -50%);
  will-change: left, top;
  transition: opacity 0.12s ease;
}
.cat-paw.is-clickable { opacity: 0.6; filter: grayscale(0.3); }
.paw-inner {
  width: 36px; height: 36px;
  position: relative;
  animation: paw-bob 2.5s ease-in-out infinite;
}
@keyframes paw-bob {
  0%,100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

/* 主肉垫 */
.paw-pad {
  position: absolute;
  bottom: 2px; left: 50%;
  transform: translateX(-50%);
  width: 16px; height: 12px;
  background: radial-gradient(ellipse at 50% 40%, #FFB6D9, #FF69B4 80%);
  border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
  box-shadow:
    0 0 10px rgba(255,105,180,0.7),
    0 0 20px rgba(255,105,180,0.35),
    inset 0 1px 3px rgba(255,255,255,0.3);
}

/* 4 个趾头 */
.paw-bean {
  position: absolute;
  width: 8px; height: 10px;
  background: radial-gradient(ellipse at 50% 30%, #FFB6D9, #FF69B4 80%);
  border-radius: 50%;
  box-shadow:
    0 0 8px rgba(255,105,180,0.6),
    inset 0 1px 2px rgba(255,255,255,0.25);
}
.paw-bean.b1 { bottom: 12px; left: 1px; transform: rotate(-25deg); }
.paw-bean.b2 { bottom: 16px; left: 8px; transform: rotate(-8deg); }
.paw-bean.b3 { bottom: 16px; right: 8px; transform: rotate(8deg); }
.paw-bean.b4 { bottom: 12px; right: 1px; transform: rotate(25deg); }

/* ── 拖尾图层 ── */
.trail-layer { position: fixed; inset: 0; pointer-events: none; z-index: 99998; }
.sakura { will-change: transform, opacity; }

/* ── Parallax BG Particles ── */
.parallax-bg { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
.par-p {
  position: absolute; bottom: -20px;
  animation: float-up linear infinite;
}
.par-star {
  position: absolute; bottom: -30px;
  animation: float-up-spin linear infinite;
}
@keyframes float-up {
  0% { transform: translateY(0) scale(0); opacity: 0; }
  15% { opacity: 1; }
  85% { opacity: 0.7; }
  100% { transform: translateY(-105vh) scale(1.3); opacity: 0; }
}
@keyframes float-up-spin {
  0% { transform: translateY(0) rotate(0deg) scale(0); opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 0.5; }
  100% { transform: translateY(-105vh) rotate(360deg) scale(1.2); opacity: 0; }
}

/* ── Navbar ── */
.navbar {
  position: sticky; top: 0; z-index: 100;
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 36px;
  background: rgba(26,20,50,0.95);
  border-bottom: 1px solid rgba(255,105,180,0.15);
}
.nav-brand { display: flex; align-items: center; gap: 10px; }
.brand-deco {
  font-size: 18px; letter-spacing: -2px;
  background: linear-gradient(135deg, var(--pink), var(--purple), var(--blue));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: breathe 3s ease-in-out infinite;
}
.navbar h1 {
  font-size: 19px; font-weight: 800; letter-spacing: 1px;
  background: linear-gradient(90deg, var(--pink), var(--blue), var(--purple));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.nav-links { display: flex; gap: 6px; }
.nav-links a {
  position: relative;
  color: var(--text2); text-decoration: none;
  padding: 9px 20px; border-radius: var(--r-pill);
  font-size: 13px; font-weight: 600;
  display: flex; align-items: center; gap: 6px;
  transition: all 0.35s cubic-bezier(0.34,1.56,0.64,1);
}
.nav-links a:hover {
  color: #fff;
  background: rgba(255,105,180,0.12);
  transform: scale(1.05);
}
.nav-links a.router-link-active {
  color: #fff;
  background: linear-gradient(135deg, rgba(255,105,180,0.25), rgba(102,204,255,0.2));
  box-shadow: 0 0 22px rgba(255,105,180,0.3);
}
.nav-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--pink);
  box-shadow: 0 0 8px var(--pink-g);
  animation: breathe 2s ease-in-out infinite;
}
.nav-links a:nth-child(2) .nav-dot { background: var(--blue); box-shadow: 0 0 8px var(--blue-g); }
.nav-links a:nth-child(3) .nav-dot { background: var(--purple); box-shadow: 0 0 8px var(--purple-g); }

@keyframes breathe {
  0%,100% { opacity: 0.6; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.25); }
}

/* ── Page transition ── */
.page-bounce-enter-active { animation: bounce-in 0.45s ease-out; }
.page-bounce-leave-active { animation: bounce-in 0.25s ease-in reverse; }
@keyframes bounce-in {
  0% { opacity: 0; transform: scale(0.92) translateY(18px); }
  60% { transform: scale(1.02) translateY(-2px); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

/* ── Main ── */
main { position: relative; z-index: 1; padding: 18px 24px 0; }
</style>
