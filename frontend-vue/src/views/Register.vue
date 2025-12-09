<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <div class="bg-gray-50 h-screen flex items-center justify-center">
    <div class="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md border border-gray-100">
      <h1 class="text-2xl font-bold text-center mb-6">创建新账号</h1>
      
      <form @submit.prevent="handleRegister" class="space-y-4">
        <div id="error-msg" :class="['bg-red-50 text-red-500 text-sm p-3 rounded-lg', { hidden: !errorMsg }]">
          {{ errorMsg }}
        </div>
        
        <input 
          type="text" 
          v-model="username" 
          class="w-full px-4 py-3 border rounded-xl outline-none focus:border-blue-500" 
          placeholder="用户名" 
          required
        >
        <input 
          type="email" 
          v-model="email" 
          class="w-full px-4 py-3 border rounded-xl outline-none focus:border-blue-500" 
          placeholder="邮箱" 
          required
        >
        <input 
          type="password" 
          v-model="password" 
          class="w-full px-4 py-3 border rounded-xl outline-none focus:border-blue-500" 
          placeholder="密码" 
          required
        >
        
        <button 
          type="submit" 
          id="submit-btn" 
          class="w-full bg-gray-900 text-white py-3.5 rounded-xl font-bold hover:bg-black transition-all"
          :disabled="isLoading"
        >
          {{ isLoading ? '注册中...' : '注册并登录' }}
        </button>
      </form>
      
      <div class="mt-6 text-center text-sm text-gray-500">
        已有账号? <router-link to="/login" class="text-blue-600 font-bold hover:underline">直接登录</router-link>
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
const email = ref('')
const password = ref('')
const isLoading = ref(false)
const errorMsg = ref('')

// 组件挂载时初始化
onMounted(() => {
  // 不需要手动设置API基础URL，使用默认的相对路径让请求走代理
})

// 邮箱验证
const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// 处理注册
const handleRegister = async () => {
  isLoading.value = true
  errorMsg.value = ''
  
  try {
    // 验证表单数据
    if (!username.value || !email.value || !password.value) {
      throw new Error('请填写所有必填字段')
    }
    
    if (!isValidEmail(email.value)) {
      throw new Error('请输入有效的邮箱地址')
    }
    
    // 1. 注册
    const registerData = await apiService.post('/auth/register', {
      username: username.value,
      email: email.value,
      password: password.value
    })

    // 2. 自动登录
    const loginData = await apiService.post('/auth/login', {
      username: username.value,
      password: password.value
    })
    
    AuthService.setSession(loginData)
    
    // 注册成功，跳转到首页
    router.push('/')
  } catch (error) {
    errorMsg.value = error.message
  } finally {
    // 无论成功或失败，都重置加载状态
    isLoading.value = false
  }
}
</script>