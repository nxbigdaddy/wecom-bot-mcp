import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: () => import('@/components/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '控制台' }
      },
      {
        path: 'send-message',
        name: 'SendMessage',
        component: () => import('@/views/SendMessage.vue'),
        meta: { title: '发送消息' }
      },
      {
        path: 'history',
        name: 'History',
        component: () => import('@/views/History.vue'),
        meta: { title: '发送历史' }
      },
      {
        path: 'scheduler',
        name: 'Scheduler',
        component: () => import('@/views/Scheduler.vue'),
        meta: { title: '定时任务' }
      },
      {
        path: 'hr-integration',
        name: 'HRIntegration',
        component: () => import('@/views/HRIntegration.vue'),
        meta: { title: 'HR 数据集成' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/Users.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: 'wecom-config',
        name: 'WeComConfig',
        component: () => import('@/views/WeComConfig.vue'),
        meta: { title: '企业微信配置' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '系统设置' }
      },
      {
        path: 'resource-manager',
        name: 'ResourceManager',
        component: () => import('@/views/ResourceManager.vue'),
        meta: { title: '资源管理' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '页面未找到' }
  }
]

const router = createRouter({
  history: createWebHistory('/'),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title} - WeCom Bot Server`
  
  // 检查是否需要登录
  if (to.meta.requiresAuth || to.path !== '/login') {
    const token = YOUR_SECRET'token')
    if (!token && to.path !== '/login') {
      next({ name: 'Login', query: { redirect: to.fullPath } })
    } else if (token && to.path === '/login') {
      // 如果已登录，访问登录页则跳转到首页
      next({ name: 'Dashboard' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
