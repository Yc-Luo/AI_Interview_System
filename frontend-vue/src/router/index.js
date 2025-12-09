// 路由配置

// 直接导入页面组件，不使用懒加载
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import GuestInterview from '../views/GuestInterview.vue'
import OutlineList from '../views/OutlineList.vue'
import OutlineEdit from '../views/OutlineEdit.vue'
import AIConfig from '../views/AIConfig.vue'
import InterviewList from '../views/InterviewList.vue'
import InterviewDetail from '../views/InterviewDetail.vue'
import Settings from '../views/Settings.vue'

// 路由配置数组
const routes = [
  // 认证相关路由 - 无需登录即可访问
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false, layout: 'empty' }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresAuth: false, layout: 'empty' }
  },
  
  // 嘉宾访谈相关路由 - 无需登录即可访问
  {
    path: '/guest-interview',
    name: 'GuestInterview',
    component: GuestInterview,
    meta: { requiresAuth: false, layout: 'empty' }
  },
  
  // 主应用路由 - 放在最后，使用懒加载
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/home',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: false, layout: 'main' }
  },
  {
    path: '/outline-list',
    name: 'OutlineList',
    component: OutlineList,
    meta: { requiresAuth: true, layout: 'main' }
  },
  {
    path: '/outline-edit',
    name: 'OutlineEdit',
    component: OutlineEdit,
    meta: { requiresAuth: true, layout: 'main' }
  },
  {
    path: '/ai-config',
    name: 'AIConfig',
    component: AIConfig,
    meta: { requiresAuth: true, layout: 'main' }
  },
  {
    path: '/interview-list',
    name: 'InterviewList',
    component: InterviewList,
    meta: { requiresAuth: true, layout: 'main' }
  },
  { path: '/interview-detail',
    name: 'InterviewDetail',
    component: InterviewDetail,
    meta: { requiresAuth: true, layout: 'main' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: { requiresAuth: true, layout: 'main' }
  }
]

export default routes
