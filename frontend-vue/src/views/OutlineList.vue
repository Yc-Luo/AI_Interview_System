<template>
  <div>
    <!-- 标题和操作按钮 -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-800">我的访谈提纲</h2>
        <p class="text-gray-500 mt-1">管理和编辑您的所有访谈设计</p>
      </div>
      <router-link to="/outline-edit" class="bg-primary hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl font-bold shadow-lg shadow-blue-500/30 transition-all flex items-center gap-2 active:scale-95">
        <i class="fas fa-plus"></i>
        新建提纲
      </router-link>
    </div>

    <!-- 搜索和过滤 -->
    <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-200 mb-6 flex flex-col md:flex-row gap-4">
      <div class="relative flex-1">
        <i class="fas fa-search absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="搜索提纲名称..." 
          class="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-primary"
        >
      </div>
      <div class="flex gap-2">
        <select v-model="sortType" class="px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-600 focus:outline-none focus:border-primary cursor-pointer">
          <option value="newest">按创建时间 (最新)</option>
          <option value="oldest">按创建时间 (最早)</option>
        </select>
      </div>
    </div>

    <!-- 提纲列表 -->
    <div v-if="outlines.length > 0" class="grid grid-cols-1 gap-4">
      <div 
        v-for="outline in filteredOutlines" 
        :key="outline.id" 
        class="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 outline-card cursor-pointer group hover:shadow-md transition-all"
        @click="goToEdit(outline.id)"
      >
        <div class="flex justify-between items-start">
          <div class="flex items-start gap-4">
            <div class="w-12 h-12 bg-blue-50 text-primary rounded-xl flex items-center justify-center flex-shrink-0 group-hover:bg-primary group-hover:text-white transition-colors">
              <i class="fas fa-file-alt text-xl"></i>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-800 group-hover:text-primary transition-colors">{{ outline.title }}</h3>
              <p class="text-xs text-gray-400 mt-1"><i class="far fa-clock mr-1"></i>{{ formatDateTime(outline.created_at) }}</p>
              <p class="text-sm text-gray-500 mt-2 line-clamp-1">{{ outline.description || '暂无描述' }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button 
              @click.stop="openAIConfig(outline.id)" 
              class="p-2 text-gray-400 hover:text-primary hover:bg-blue-50 rounded-full transition-colors"
              title="配置 AI"
            >
              <i class="fas fa-robot"></i>
            </button>
            <button 
              @click.stop="openDeleteModal(outline.id)" 
              class="p-2 text-gray-400 hover:text-danger hover:bg-red-50 rounded-full transition-colors"
              title="删除"
            >
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="flex flex-col items-center justify-center py-20 text-center">
      <div class="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mb-4 text-gray-400 text-3xl">
        <i class="fas fa-folder-open"></i>
      </div>
      <h3 class="text-lg font-bold text-gray-700">暂无访谈提纲</h3>
      <p class="text-gray-500 text-sm mt-1 mb-6">您还没有创建任何访谈提纲，赶快开始吧！</p>
      <router-link to="/outline-edit" class="text-primary font-bold hover:underline">创建第一个提纲</router-link>
    </div>

    <!-- 删除确认弹窗 -->
    <div id="delete-modal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" v-show="showDeleteModal">
      <div class="bg-white rounded-2xl p-6 w-full max-w-sm shadow-2xl">
        <div class="text-center">
          <div class="w-14 h-14 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4 text-danger text-2xl">
            <i class="fas fa-trash-alt"></i>
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-2">确认删除？</h3>
          <p class="text-sm text-gray-500 mb-6">该操作无法撤销，对应的访谈记录可能也会受到影响。</p>
          <div class="flex gap-3">
            <button @click="closeDeleteModal" class="flex-1 py-2.5 border border-gray-300 rounded-xl text-gray-600 font-medium hover:bg-gray-50">取消</button>
            <button @click="confirmDelete" class="flex-1 py-2.5 bg-danger text-white rounded-xl font-medium hover:bg-red-600">删除</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/* eslint-disable */
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '../services/api'
import AuthService from '../services/auth'

const router = useRouter()

// 响应式数据
const outlines = ref([])
const searchQuery = ref('')
const sortType = ref('newest')
const showDeleteModal = ref(false)
const deleteTargetId = ref(null)
const isLoading = ref(false)

// 格式化日期时间
const formatDateTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', { hour12: false })
}

// 过滤与排序后的提纲列表
const filteredOutlines = computed(() => {
  // 过滤
  let filtered = outlines.value.filter(item => item.title.toLowerCase().includes(searchQuery.value.toLowerCase()))
  
  // 排序
  filtered.sort((a, b) => {
    const dateA = new Date(a.created_at)
    const dateB = new Date(b.created_at)
    return sortType.value === 'newest' ? dateB - dateA : dateA - dateB
  })
  
  return filtered
})

// 获取提纲列表
const fetchOutlines = async () => {
  isLoading.value = true
  try {
    const response = await apiService.get('/outlines/')
    outlines.value = response.items || []
  } catch (error) {
    console.error('获取提纲列表失败:', error)
    // 使用模拟数据
    outlines.value = [
      {
        id: 1,
        title: '2024届毕业生就业意向调研',
        description: '了解应届毕业生的就业方向和期望',
        question_count: 12,
        response_count: 45,
        created_at: '2024-01-15T10:30:00Z',
        status: 'active'
      },
      {
        id: 2,
        title: '大学生职业规划现状',
        description: '调查大学生职业规划的现状和需求',
        question_count: 8,
        response_count: 28,
        created_at: '2024-01-10T14:20:00Z',
        status: 'active'
      },
      {
        id: 3,
        title: '实习经历对就业的影响',
        description: '分析实习经历对就业竞争力的影响',
        question_count: 10,
        response_count: 36,
        created_at: '2024-01-05T09:15:00Z',
        status: 'draft'
      }
    ]
  } finally {
    isLoading.value = false
  }
}

// 跳转到编辑页面
const goToEdit = (outlineId) => {
  router.push(`/outline-edit?outlineId=${outlineId}`)
}

// 打开AI配置页面
const openAIConfig = (outlineId) => {
  router.push(`/ai-config?outlineId=${outlineId}`)
}

// 打开删除确认弹窗
const openDeleteModal = (outlineId) => {
  deleteTargetId.value = outlineId
  showDeleteModal.value = true
}

// 关闭删除确认弹窗
const closeDeleteModal = () => {
  showDeleteModal.value = false
  deleteTargetId.value = null
}

// 确认删除提纲
const confirmDelete = async () => {
  if (!deleteTargetId.value) return
  
  try {
    // 发送删除请求
    await apiService.delete(`/outlines/${deleteTargetId.value}`)
    
    // 更新 UI
    outlines.value = outlines.value.filter(item => item.id !== deleteTargetId.value)
    closeDeleteModal()
    alert('提纲删除成功')
  } catch (e) {
    console.error('删除失败:', e)
    alert(`删除失败: ${e.message}`)
    fetchOutlines() // 回滚
  }
}

// 组件挂载时初始化
onMounted(() => {
  // 登录守卫
  if (!AuthService.isLoggedIn()) {
    router.push('/login')
  }
  
  // 获取提纲列表
  fetchOutlines()
})
</script>

<style scoped>
.card-hover {
  transition: all 0.2s ease-in-out;
}

.card-hover:hover {
  transform: translateY(-4px);
}

.outline-card {
  border-left: 4px solid transparent;
  transition: all 0.2s;
}

.outline-card:hover {
  border-left-color: #2563eb;
}
</style>