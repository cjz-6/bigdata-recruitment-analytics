import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
  { path: '/jobs', name: 'Jobs', component: () => import('../views/Jobs.vue') },
  { path: '/ai', name: 'AIChat', component: () => import('../views/AIChat.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
