<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <div class="bg-gray-50 h-screen flex items-center justify-center">
    <div class="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md border border-gray-100">
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold text-gray-800">欢迎回来</h1>
        <p class="text-gray-500 text-sm mt-2">登录以管理您的访谈项目</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-5">
        <div id="error-msg" :class="['bg-red-50 text-red-500 text-sm p-3 rounded-lg flex items-center gap-2', { hidden: !errorMsg }]">
          <i class="fas fa-exclamation-circle"></i><span>{{ errorMsg }}</span>
        </div>
        
        <input 
          type="text" 
          v-model="username" 
          class="w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 outline-none" 
          placeholder="用户名 (admin)" 
          required
        >
        <input 
          type="password" 
          v-model="password" 
          class="w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 outline-none" 
          placeholder="密码 (admin123)" 
          required
        >
        
        <button 
          type="submit" 
          id="submit-btn" 
          class="w-full bg-blue-600 text-white py-3.5 rounded-xl font-bold hover:bg-blue-700 transition-all"
          :disabled="isLoading"
        >
          {{ isLoading ? '登录中...' : '立即登录' }}
        </button>
      </form>

      <div class="mt-6 text-center text-sm text-gray-500">
        还没有账号? <router-link to="/register" class="text-blue-600 font-bold hover:underline">去注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
/* eslint-disable */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '../services/api'
import AuthService from '../services/auth'

const router = useRouter()

// 响应式数据
const username = ref('')
const password = ref('')
const isLoading = ref(false)
const errorMsg = ref('')

// 组件挂载时初始化
onMounted(() => {
  // 检查登录状态
  if (AuthService.isLoggedIn()) {
    if (window.location.protocol !== 'blob:') {
      router.push('/')
    }
  }
})

// 处理登录
const handleLogin = async () => {
  isLoading.value = true
  errorMsg.value = ''
  
  try {
    // 使用统一的API请求封装
    const data = await apiService.post('/auth/login', {
      username: username.value,
      password: password.value
    })

    AuthService.setSession(data)
    
    // 登录成功，跳转到首页
    const redirect = sessionStorage.getItem('redirect_after_login') || '/' 
    sessionStorage.removeItem('redirect_after_login')
    router.push(redirect)
  } catch (error) {
    errorMsg.value = error.message
  } finally {
    // 无论成功或失败，都重置加载状态
    isLoading.value = false
  }
}
</script>