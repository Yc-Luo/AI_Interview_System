<!-- eslint-disable vue/multi-word-component-names -->
<template>
    <!-- 欢迎语 & 快速开始 -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-10 gap-4">
        <div>
            <h2 class="text-2xl font-bold text-gray-800" id="welcome-message">{{ welcomeMessage }}</h2>
            <p class="text-gray-500 mt-1">这里是您的访谈控制中心，管理提纲与数据。</p>
        </div>
        <router-link to="/outline-edit" class="bg-primary hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-bold shadow-lg shadow-blue-500/30 transition-all flex items-center gap-2 active:scale-95">
            <i class="fas fa-plus"></i>
            创建新访谈
        </router-link>
    </div>

    <!-- 核心数据卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <!-- 提纲卡片 -->
        <router-link to="/outline-list" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 card-hover cursor-pointer group relative overflow-hidden">
            <div class="absolute right-0 top-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                <i class="fas fa-file-alt text-6xl text-blue-600"></i>
            </div>
            <div class="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center mb-4 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                <i class="fas fa-file-alt text-xl"></i>
            </div>
            <p class="text-sm text-gray-500 font-medium">我的提纲</p>
            <div class="flex items-end gap-2 mt-1">
                <p class="text-3xl font-bold text-gray-800" id="outline-count">{{ outlineCount }}</p>
                <span class="text-sm text-gray-400 mb-1">个项目</span>
            </div>
        </router-link>

        <!-- 访谈会话卡片 -->
        <router-link to="/interview-list" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 card-hover cursor-pointer group relative overflow-hidden">
            <div class="absolute right-0 top-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                <i class="fas fa-comments text-6xl text-green-500"></i>
            </div>
            <div class="w-12 h-12 bg-green-50 text-green-600 rounded-xl flex items-center justify-center mb-4 group-hover:bg-green-600 group-hover:text-white transition-colors">
                <i class="fas fa-comments text-xl"></i>
            </div>
            <p class="text-sm text-gray-500 font-medium">已收集样本</p>
            <div class="flex items-end gap-2 mt-1">
                <p class="text-3xl font-bold text-gray-800" id="session-count">{{ sessionCount }}</p>
                <span class="text-sm text-gray-400 mb-1">份记录</span>
            </div>
        </router-link>

        <!-- 正在运行卡片 -->
        <div class="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-6 shadow-lg text-white card-hover cursor-pointer relative overflow-hidden">
            <div class="absolute right-0 bottom-0 p-4 opacity-20">
                <i class="fas fa-rocket text-6xl"></i>
            </div>
            <div class="relative z-10">
                <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mb-4 backdrop-blur-sm">
                    <i class="fas fa-broadcast-tower text-xl"></i>
                </div>
                <p class="text-indigo-100 font-medium text-sm">系统状态</p>
                <p class="text-2xl font-bold mt-1">运行正常</p>
                <p class="text-xs text-indigo-200 mt-2">点击查看监控看板 &rarr;</p>
            </div>
        </div>
    </div>

    <!-- 最近活动 -->
    <section class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-bold text-gray-800 flex items-center gap-2">
                <i class="fas fa-history text-gray-400"></i> 最近活动
            </h3>
        </div>
        
        <div v-if="activities.length > 0" id="activity-list" class="space-y-4">
            <!-- 动态活动项 -->
            <div v-for="activity in activities" :key="activity.id" @click="handleActivityClick(activity)" class="flex items-start gap-4 p-3 hover:bg-gray-50 rounded-lg transition-colors group cursor-pointer border-l-4 border-transparent hover:border-blue-500">
                <div :class="['w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0', getActivityColor(activity.color)]">
                    <i :class="['fas', activity.icon]"></i>
                </div>
                <div class="flex-1">
                    <p class="text-sm font-bold text-gray-800 group-hover:text-primary transition-colors">
                      {{ activity.title }} <span v-if="activity.content">{{ activity.content }}</span>
                    </p>
                    <p v-if="activity.description" class="text-xs text-gray-500 mt-1">{{ activity.description }}</p>
                </div>
                <span class="text-xs text-gray-400 whitespace-nowrap">{{ activity.time }}</span>
            </div>
        </div>
        
        <!-- 空状态 -->
        <div v-else id="activity-empty" class="flex flex-col items-center justify-center py-12 text-center">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4 text-gray-400 text-2xl">
                <i class="fas fa-clock"></i>
            </div>
            <h4 class="text-lg font-bold text-gray-700 mb-2">暂无活动记录</h4>
            <p class="text-gray-500 text-sm">开始创建您的第一个访谈提纲，记录将显示在这里</p>
        </div>
    </section>
</template>

<script setup>
/* eslint-disable */
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '../services/api'
import AuthService from '../services/auth'

const router = useRouter()

// 响应式数据
const username = ref('')
const outlineCount = ref('-')
const sessionCount = ref('-')
const activities = ref([])

// 计算属性：欢迎消息
const welcomeMessage = computed(() => {
  if (!username.value) return '欢迎回来，开始您的研究'
  
  const now = new Date()
  const hour = now.getHours()
  
  let greeting = ''
  if (hour < 6) {
    greeting = '夜深了，注意休息'
  } else if (hour < 12) {
    greeting = '早上好'
  } else if (hour < 18) {
    greeting = '下午好'
  } else {
    greeting = '晚上好'
  }
  
  return `${greeting}，${username.value}`
})

// 获取活动项颜色
const getActivityColor = (color) => {
  const colorMap = {
    'blue': 'bg-blue-100 text-blue-600',
    'green': 'bg-green-100 text-green-600',
    'purple': 'bg-purple-100 text-purple-600',
    'orange': 'bg-orange-100 text-orange-600'
  }
  return colorMap[color] || 'bg-gray-100 text-gray-600'
}

// 获取首页数据
const fetchDashboardData = async () => {
  try {
    // 真实请求：获取提纲列表
    const outlineResponse = await apiService.get('/outlines')
    
    // 正确处理API响应数据结构
    let outlineList = []
    if (Array.isArray(outlineResponse)) {
      // 直接返回了提纲列表
      outlineList = outlineResponse
    } else if (outlineResponse && typeof outlineResponse === 'object') {
      // 检查是否有items属性
      if (outlineResponse.items && Array.isArray(outlineResponse.items)) {
        // 返回了包含items的对象
        outlineList = outlineResponse.items
      } else {
        // 可能是其他结构，尝试获取数据
        outlineList = []
      }
    }
    outlineCount.value = outlineList.length || 0
    
    // 获取会话统计 - 尝试获取所有会话，然后统计数量
    try {
      const sessionsResponse = await apiService.get('/sessions')
      
      // 正确处理API响应数据结构
      let sessionsList = []
      if (Array.isArray(sessionsResponse)) {
        // 直接返回了会话列表
        sessionsList = sessionsResponse
      } else if (sessionsResponse && typeof sessionsResponse === 'object') {
        // 检查是否有items属性
        if (sessionsResponse.items && Array.isArray(sessionsResponse.items)) {
          // 返回了包含items的对象
          sessionsList = sessionsResponse.items
        } else {
          // 可能是其他结构，尝试获取数据
          sessionsList = []
        }
      }
      sessionCount.value = sessionsList.length || 0
    } catch (error) {
      console.error("加载会话统计失败:", error)
      sessionCount.value = 0
    }
  } catch (error) {
    console.error("加载数据失败:", error)
    outlineCount.value = 0 
    sessionCount.value = 0 
  }
}

// 获取最近活动
const fetchRecentActivities = async () => {
  try {
    // 真实请求：获取最近活动
    const activitiesResponse = await apiService.get('/activities/')
    // 检查activitiesResponse的类型和结构
    if (Array.isArray(activitiesResponse)) {
      // 直接返回了活动列表
      activities.value = activitiesResponse
    } else if (activitiesResponse && typeof activitiesResponse === 'object') {
      // 检查是否有items属性
      if (activitiesResponse.items && Array.isArray(activitiesResponse.items)) {
        // 返回了包含items的对象
        activities.value = activitiesResponse.items
      } else {
        // 可能是直接返回的单个活动对象，包装成数组
        activities.value = [activitiesResponse]
      }
    } else {
      // 数据格式不符合预期，清空活动列表
      activities.value = []
      console.error("获取活动数据失败: 数据格式不符合预期")
    }
  } catch (error) {
    console.error("加载活动数据失败:", error)
    // API调用失败，清空活动列表
    activities.value = []
  }
}

// 活动点击处理
const handleActivityClick = (activity) => {
  // 根据活动类型跳转到不同页面
  switch (activity.type) {
    case 'create_outline':
      router.push('/outline-list')
      break
    case 'receive_session':
      router.push('/interview-list')
      break
    case 'update_ai_config':
      router.push('/ai-config')
      break
    default:
      // 默认跳转到首页
      router.push('/')
  }
}

// 实时更新定时器
let activityUpdateTimer = null

// 组件挂载时初始化
onMounted(() => {
  // 显示默认用户名
  username.value = AuthService.getUsername() || '管理员'

  // 加载仪表盘数据
  fetchDashboardData()
  // 加载最近活动
  fetchRecentActivities()
  
  // 设置实时更新定时器（每30秒更新一次）
  activityUpdateTimer = setInterval(() => {
    // 同时更新核心数据和最近活动
    fetchDashboardData()
    fetchRecentActivities()
  }, 30000)
})

// 组件卸载时清理
onBeforeUnmount(() => {
  if (activityUpdateTimer) {
    clearInterval(activityUpdateTimer)
  }
})
</script>