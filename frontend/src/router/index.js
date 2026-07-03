import { createRouter, createWebHistory } from 'vue-router'
import { isLoggedIn } from '../api/auth'
import Login from '../views/Login.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { public: true }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/records',
    name: 'Records',
    component: () => import('../views/Records.vue')
  },
  {
    path: '/alert-logs',
    name: 'AlertLogs',
    component: () => import('../views/AlertLogs.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.public) {
    if (to.path === '/login' && isLoggedIn()) {
      next('/')
      return
    }
    next()
    return
  }
  if (!isLoggedIn()) {
    next('/login')
    return
  }
  next()
})

export default router
