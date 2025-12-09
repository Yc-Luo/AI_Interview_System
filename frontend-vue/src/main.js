import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import './index.css'
import App from './App.vue'

// 导入路由配置
import routes from './router'
import useUserStore from './store/user'

// 创建Vue应用实例
const app = createApp(App)

// 创建Pinia实例
const pinia = createPinia()

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 使用插件
app.use(pinia)
app.use(router)

// 添加路由守卫 - 必须在使用插件后添加
router.beforeEach((to, from, next) => {
  // 获取用户状态
  const userStore = useUserStore()
  const isLoggedIn = userStore.isLoggedIn
  
  // 检查路由是否需要认证
  if (to.meta.requiresAuth && !isLoggedIn) {
    // 需要认证但未登录，跳转到登录页面
    next('/login')
  } else {
    // 不需要认证或已登录，继续导航
    next()
  }
})

// 挂载应用
app.mount('#app')
