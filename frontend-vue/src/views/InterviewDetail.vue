<template>
  <div>
    <!-- 页面标题栏 -->
  <div class="flex items-center gap-4 mb-6 pb-4 border-b">
    <button @click="goBack" class="w-10 h-10 rounded-lg hover:bg-gray-100 flex items-center justify-center transition-colors">
      <i class="fas fa-arrow-left text-gray-600"></i>
    </button>
      <div class="flex items-center gap-2">
        <h1 class="text-xl font-bold text-gray-800" id="project-name">{{ projectName }}</h1>
        <span class="flex items-center text-sm text-green-600 font-medium">
          <span class="status-indicator status-running"></span>
          进行中
        </span>
      </div>
    </div>

    <!-- 主内容 -->
    <div class="mb-6 gap-4">
        <!-- 操作栏 -->
        <div class="flex flex-wrap justify-between items-center mb-6 gap-4">
            <div class="flex gap-2">
                <button id="export-selected" @click="exportSelected" class="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium">
                    导出选中内容
                </button>
                <button id="delete-selected" @click="deleteSelected" class="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium">
                    删除选中内容
                </button>
            </div>
            <div class="flex gap-2">
                <button id="clear-all" @click="clearAll" class="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium flex items-center gap-2">
                    <i class="fas fa-trash text-gray-500"></i>
                    清空全部
                </button>
                <div class="relative">
                    <button id="download-all" @click="toggleDownloadDropdown" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium flex items-center gap-2">
                        <i class="fas fa-download"></i>
                        下载访谈内容
                        <i class="fas fa-chevron-down text-xs"></i>
                    </button>
                    <div id="download-dropdown" class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-10" :class="{ hidden: !isDownloadDropdownOpen }">
                        <button class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 download-format" @click="downloadContent('excel')">Excel格式</button>
                        <button class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 download-format" @click="downloadContent('pdf')">PDF格式</button>
                        <button class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 download-format" @click="downloadContent('csv')">CSV格式</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 数据可视化区域 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
            <h2 class="text-xl font-bold text-gray-800 mb-6">数据统计与可视化</h2>
            
            <!-- 统计卡片 -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <div class="bg-blue-50 rounded-lg p-4 border border-blue-100">
                    <p class="text-sm text-blue-600 font-medium">总访谈数</p>
                    <p class="text-3xl font-bold text-blue-900" id="stat-total">{{ totalInterviews }}</p>
                </div>
                <div class="bg-green-50 rounded-lg p-4 border border-green-100">
                    <p class="text-sm text-green-600 font-medium">已完成</p>
                    <p class="text-3xl font-bold text-green-900" id="stat-completed">{{ completedInterviews }}</p>
                </div>
                <div class="bg-yellow-50 rounded-lg p-4 border border-yellow-100">
                    <p class="text-sm text-yellow-600 font-medium">进行中</p>
                    <p class="text-3xl font-bold text-yellow-900" id="stat-active">{{ activeInterviews }}</p>
                </div>
                <div class="bg-purple-50 rounded-lg p-4 border border-purple-100">
                    <p class="text-sm text-purple-600 font-medium">平均时长(秒)</p>
                    <p class="text-3xl font-bold text-purple-900" id="stat-average">{{ averageDuration }}</p>
                </div>
            </div>
            
            <!-- 图表区域 -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- 访谈数量趋势图 -->
                <div class="bg-white rounded-lg p-4 border border-gray-200">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">访谈数量趋势</h3>
                    <div class="h-32">
                        <canvas id="interview-trend-chart"></canvas>
                    </div>
                </div>
                <!-- 访谈状态饼图 -->
                <div class="bg-white rounded-lg p-4 border border-gray-200">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">访谈状态分布</h3>
                    <div class="h-32">
                        <canvas id="interview-status-chart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- 访谈对话详情弹窗 -->
        <div id="dialog-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 hidden">
            <div class="bg-white rounded-xl shadow-lg w-full max-w-4xl h-[80vh] flex flex-col">
                <!-- 弹窗头部 -->
                <div class="flex justify-between items-center p-6 border-b">
                    <div>
                        <h3 class="text-lg font-bold text-gray-900">{{ projectName }}</h3>
                        <div class="flex items-center mt-1">
                            <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold mr-2">{{ participantName.charAt(0) }}</div>
                            <span class="text-sm text-gray-600">{{ participantName }} - {{ participantInfo }}</span>
                        </div>
                    </div>
                    <div class="flex items-center gap-4">
                        <button id="dialog-star-btn" @click="toggleStarDialog" class="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium flex items-center gap-2">
                            <i id="dialog-star-icon" :class="['far', currentInterview?.is_starred ? 'fas text-yellow-500' : 'far']" class="fa-star"></i>
                            星标
                        </button>
                        <button id="dialog-delete-btn" @click="deleteDialog" class="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium flex items-center gap-2">
                            <i class="far fa-trash-alt"></i>
                            删除
                        </button>
                        <button id="dialog-export-btn" @click="exportDialog" class="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium flex items-center gap-2">
                            <i class="fas fa-file-export"></i>
                            导出
                        </button>
                        <button id="close-dialog-modal" @click="closeDialogModal" class="text-gray-500 hover:text-gray-700">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                
                <!-- 对话内容 -->
                <div id="dialog-content" class="flex-1 p-6 overflow-y-auto space-y-6">
                    <!-- 对话内容将通过JavaScript动态生成 -->
                    <div v-if="currentDialog.length === 0" class="text-center py-8 text-gray-500">
                        <i class="fas fa-comments mr-2"></i> 暂无对话内容
                    </div>
                    <div v-else>
                        <div v-for="msg in currentDialog" :key="msg.id" :class="['flex', msg.role === 'ai' ? 'justify-start' : 'justify-end']">
                            <div class="max-w-[70%] p-4 rounded-lg" :class="msg.role === 'ai' ? 'bg-blue-100 text-blue-900 rounded-tl-none' : 'bg-blue-600 text-white rounded-tr-none'">
                                {{ msg.content }}
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 弹窗底部 -->
                <div class="flex justify-between items-center p-6 border-t">
                    <div class="flex items-center gap-2">
                        <button @click="showPreviousInterview" class="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium">上一份</button>
                        <button @click="showNextInterview" class="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium">下一份</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 备注弹窗 -->
        <div id="note-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" :class="{ hidden: !isNoteModalVisible }">
            <div class="bg-white rounded-xl shadow-lg p-6 w-full max-w-md">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-bold text-gray-900">添加备注</h3>
                    <button id="close-note-modal" @click="closeNoteModal" class="text-gray-500 hover:text-gray-700">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <textarea id="note-content" v-model="currentNoteContent" class="w-full border border-gray-300 rounded-lg p-3 h-32 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="请输入备注内容..."></textarea>
                <div class="flex justify-end gap-2 mt-4">
                    <button id="cancel-note" @click="closeNoteModal" class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors">取消</button>
                    <button id="save-note" @click="saveNote" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">保存</button>
                </div>
            </div>
        </div>

        <!-- 表格容器 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="table-container w-full">
                <table class="w-full min-w-full">
                    <thead>
                        <tr>
                            <th class="w-10"><input type="checkbox" id="select-all" class="rounded text-blue-600 focus:ring-blue-500" @change="toggleSelectAll"></th>
                            <th class="w-10">星标</th> <!-- 标记重要内容 -->
                            <th class="w-10">备注</th> <!-- 备注内容，弹出备注弹窗 -->
                            <th class="w-20">查看详情</th> <!-- 只留下“眼睛”按钮，弹出访谈对话详情弹窗 -->
                            <th class="w-16">序号</th> <!-- 按开始访谈的时间先后进行增序排序，1-10-20…… -->
                            <th class="w-24">用户ID</th> <!-- 访谈用户（包括访客）的唯一UUID -->
                            <th class="w-32">开始访谈时间</th> <!-- 开始访谈时间 -->
                            <th class="w-32">结束访谈时间</th> <!-- 结束访谈时间 -->
                            <th class="w-24">所用时间</th> <!-- 访谈所用时间（分：秒） -->
                            <th class="w-24">删除</th> <!-- “垃圾桶”删除按钮 -->
                        </tr>
                    </thead>
                    <tbody id="interview-table-body">
                        <tr v-if="interviews.length === 0">
                            <td colspan="10" class="text-center py-8 text-gray-500">
                                <i class="fas fa-inbox mr-2"></i> 暂无访谈数据
                            </td>
                        </tr>
                        <tr v-else v-for="(interview, index) in interviews" :key="interview.id" :data-id="interview.id">
                            <td class="w-10"><input type="checkbox" class="row-checkbox rounded text-blue-600 focus:ring-blue-500" v-model="selectedInterviews[interview.id]"></td>
                            <td class="w-10">
                                <button class="action-btn star-btn" @click="toggleStar(interview.id)">
                                    <i :class="[interview.is_starred ? 'fas' : 'far', 'fa-star', interview.is_starred ? 'text-yellow-500' : '']"></i>
                                </button>
                            </td>
                            <td class="w-10">
                                <button class="action-btn note-btn" @click="openNoteModal(interview.id)">
                                    <i class="far fa-sticky-note"></i>
                                </button>
                            </td>
                            <td class="w-20">
                                <button class="action-btn view-btn" @click="openDialogModal(interview.id)" title="查看详情">
                                    <i class="far fa-eye text-blue-600"></i>
                                </button>
                            </td>
                            <td class="w-16 font-medium text-gray-900">{{ (currentPage - 1) * pageSize + index + 1 }}</td>
                            <td class="w-24">{{ interview.user_id || interview.visitor_uuid || 'N/A' }}</td>
                            <td class="w-32">{{ formatDateTime(interview.created_at) }}</td>
                            <td class="w-32">{{ interview.end_time ? formatDateTime(interview.end_time) : '进行中' }}</td>
                            <td class="w-24">{{ formatDuration(interview.created_at, interview.end_time) }}</td>
                            <td class="w-24">
                                <button class="action-btn delete-btn" @click="deleteInterview(interview.id)" title="删除">
                                    <i class="far fa-trash-alt text-red-600"></i>
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- 分页 -->
            <div class="px-6 py-4 bg-gray-50 border-t flex flex-wrap justify-between items-center gap-4">
                <div class="text-sm text-gray-600">
                    共 <span id="total-count">{{ interviews.length }}</span> 条
                </div>
                <div class="flex items-center gap-2">
                    <button id="first-page" class="pagination-btn" title="首页" @click="goToPage(1)">
                        &lt;&lt;
                    </button>
                    <button id="prev-page" class="pagination-btn" title="上一页" @click="goToPage(currentPage - 1)">
                        &lt;
                    </button>
                    <span class="text-sm text-gray-600">
                        <span id="current-page">{{ currentPage }}</span>/<span id="total-pages">{{ totalPages }}</span>
                    </span>
                    <button id="next-page" class="pagination-btn" title="下一页" @click="goToPage(currentPage + 1)">
                        &gt;
                    </button>
                    <button id="last-page" class="pagination-btn" title="末页" @click="goToPage(totalPages)">
                        &gt;&gt;
                    </button>
                </div>
                <div class="flex items-center gap-2">
                    <span class="text-sm text-gray-600">每页显示</span>
                    <select id="page-size" class="border rounded-lg px-2 py-1 text-sm" v-model="pageSize" @change="changePageSize">
                        <option value="10">10</option>
                        <option value="20">20</option>
                        <option value="50">50</option>
                        <option value="100">100</option>
                    </select>
                    <span class="text-sm text-gray-600">条记录</span>
                    <span class="text-sm text-gray-600">到第</span>
                    <input type="number" id="jump-page" class="border rounded-lg px-2 py-1 text-sm w-16" v-model="jumpPage" min="1" :max="totalPages">
                    <button id="jump-confirm" class="px-3 py-1 bg-gray-100 border rounded-lg text-sm hover:bg-gray-200 transition-colors" @click="goToPage(parseInt(jumpPage))">
                        确认
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiService from '../services/api'

const route = useRoute()
const router = useRouter()

// URL参数
const projectId = route.query.projectId

// 后退按钮方法
const goBack = () => {
  router.back()
}

// 响应式数据
const projectName = ref('用户体验调研项目')
const interviews = ref([])
const selectedInterviews = ref({})
const currentNoteId = ref(null)
const currentNoteContent = ref('')
const currentDialogId = ref(null)
const currentDialog = ref([])
const participantName = ref('张三')
const participantInfo = ref('计算机专业·大三')
const isDownloadDropdownOpen = ref(false)
const isNoteModalVisible = ref(false)

// 当前访谈数据
const currentInterview = ref(null)

// 分页数据
const currentPage = ref(1)
const totalPages = ref(17)
const pageSize = ref(10)
const jumpPage = ref(1)

// 统计数据
const totalInterviews = ref(0)
const completedInterviews = ref(0)
const activeInterviews = ref(0)
const averageDuration = ref(0)

// 分页计算属性
const paginatedInterviews = computed(() => {
  const start = (currentPage.value - 1) * parseInt(pageSize.value)
  const end = start + parseInt(pageSize.value)
  return interviews.value.slice(start, end)
})

// 格式化日期时间
function formatDateTime(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 格式化时长
function formatDuration(startTime, endTime) {
  if (!endTime) return '00:00'
  const start = new Date(startTime).getTime()
  const end = new Date(endTime).getTime()
  const duration = Math.floor((end - start) / 1000) // 转换为秒
  const minutes = Math.floor(duration / 60)
  const seconds = duration % 60
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
}

// 获取访谈数据
async function fetchInterviews() {
  try {
    const response = await apiService.get(`/sessions?project_id=${projectId}`)
    interviews.value = response.items || []
    
    // 按开始访谈时间增序排序
    interviews.value.sort((a, b) => {
      return new Date(a.created_at) - new Date(b.created_at)
    })
    
    updateStats()
  } catch (error) {
    console.error('获取访谈数据失败:', error)
  }
}

// 更新统计数据
function updateStats() {
  totalInterviews.value = interviews.value.length
  completedInterviews.value = interviews.value.filter(item => item.end_time !== null && item.end_time !== undefined).length
  activeInterviews.value = interviews.value.filter(item => item.end_time === null || item.end_time === undefined).length
  
  // 计算平均时长
  const totalDuration = interviews.value.reduce((sum, item) => {
    if (item.end_time) {
      const start = new Date(item.created_at).getTime()
      const end = new Date(item.end_time).getTime()
      return sum + Math.floor((end - start) / 1000) // 转换为秒
    }
    return sum
  }, 0)
  
  averageDuration.value = totalInterviews.value > 0 ? Math.round(totalDuration / totalInterviews.value) : 0
  totalPages.value = Math.ceil(totalInterviews.value / pageSize.value)
}

// 全选/取消全选
function toggleSelectAll(event) {
  const isChecked = event.target.checked
  const newSelected = {}
  if (isChecked) {
    // 全选：将所有访谈ID添加到选中对象中
    interviews.value.forEach(interview => {
      newSelected[interview.id] = true
    })
  }
  // 取消全选：newSelected为空对象
  selectedInterviews.value = newSelected
}

// 打开访谈对话详情弹窗
function openDialogModal(id) {
  currentDialogId.value = id
  const interview = interviews.value.find(item => item.id === id)
  if (interview) {
    currentInterview.value = interview
    currentDialog.value = interview.transcript || []
    participantName.value = interview.interviewee_info?.name || '匿名用户'
    participantInfo.value = interview.interviewee_info?.info || ''
    document.getElementById('dialog-modal').classList.remove('hidden')
  }
}

// 关闭访谈对话详情弹窗
function closeDialogModal() {
  document.getElementById('dialog-modal').classList.add('hidden')
}

// 切换星标状态
function toggleStarDialog() {
  if (currentInterview.value) {
    currentInterview.value.is_starred = !currentInterview.value.is_starred
    // 更新表格中对应访谈的状态
    const interviewIndex = interviews.value.findIndex(item => item.id === currentInterview.value.id)
    if (interviewIndex !== -1) {
      interviews.value[interviewIndex].is_starred = currentInterview.value.is_starred
    }
    // 保存到后端
    apiService.put(`/sessions/${currentInterview.value.id}/star`, { is_starred: currentInterview.value.is_starred })
      .catch(error => {
        console.error('更新星标状态失败:', error)
        // 恢复原状态
        currentInterview.value.is_starred = !currentInterview.value.is_starred
        if (interviewIndex !== -1) {
          interviews.value[interviewIndex].is_starred = !interviews.value[interviewIndex].is_starred
        }
      })
  }
}

// 删除访谈
function deleteDialog() {
  if (currentInterview.value && confirm('确定要删除这个访谈吗？')) {
    apiService.delete(`/sessions/${currentInterview.value.id}`)
      .then(() => {
        // 从列表中移除
        interviews.value = interviews.value.filter(item => item.id !== currentInterview.value.id)
        updateStats()
        closeDialogModal()
      })
      .catch(error => {
        console.error('删除访谈失败:', error)
        alert('删除失败，请重试')
      })
  }
}

// 导出访谈
function exportDialog() {
  if (currentInterview.value) {
    // 生成文件名
    const fileName = `访谈内容_${projectName.value}_${currentInterview.value.id.slice(0, 8)}_${new Date().toISOString().slice(0, 10)}.xlsx`
    
    // 使用新的API方法导出单个会话
    apiService.exportSingleSession(currentInterview.value.id, fileName)
      .catch(error => {
        console.error('导出访谈失败:', error)
        alert('导出失败，请重试')
      })
  }
}

// 导出选中内容
function exportSelected() {
  const selectedIds = Object.keys(selectedInterviews.value).filter(id => selectedInterviews.value[id])
  if (selectedIds.length === 0) {
    alert('请先选择要导出的内容')
    return
  }
  
  // 生成文件名
  const fileName = `访谈内容_${projectName.value}_选中_${new Date().toISOString().slice(0, 10)}.xlsx`
  
  // 使用新的API方法导出选中会话
  apiService.exportSelectedSessions(selectedIds, fileName)
    .catch(error => {
      console.error('导出选中访谈失败:', error)
      alert('导出失败，请重试')
    })
}

// 删除选中内容
function deleteSelected() {
  const selectedIds = Object.keys(selectedInterviews.value).filter(id => selectedInterviews.value[id])
  if (selectedIds.length === 0) {
    alert('请先选择要删除的内容')
    return
  }
  if (confirm('确定要删除选中的内容吗？')) {
    // 调用API删除选中内容，使用正确的DELETE请求格式
    apiService.delete(`/sessions/batch`, {
      method: 'DELETE',
      body: { ids: selectedIds },
      headers: { 'Content-Type': 'application/json' }
    })
      .then(() => {
        // 更新本地数据
        interviews.value = interviews.value.filter(item => !selectedIds.includes(item.id))
        // 清空选中状态
        selectedInterviews.value = {}
        // 更新统计数据
        updateStats()
        alert('删除成功')
      })
      .catch(error => {
        console.error('删除失败:', error)
        alert(`删除失败: ${error.message}`)
      })
  }
}

// 清空全部
function clearAll() {
  if (confirm('确定要清空全部内容吗？')) {
    // 获取当前项目的所有访谈ID
    const allIds = interviews.value.map(interview => interview.id)
    if (allIds.length === 0) {
      alert('当前没有访谈记录')
      return
    }
    // 调用API删除所有访谈记录
    apiService.delete(`/sessions/batch`, {
      method: 'DELETE',
      body: { ids: allIds },
      headers: { 'Content-Type': 'application/json' }
    })
      .then(() => {
        // 更新本地数据
        interviews.value = []
        // 清空选中状态
        selectedInterviews.value = {}
        // 更新统计数据
        updateStats()
        alert('清空成功')
      })
      .catch(error => {
        console.error('清空失败:', error)
        alert(`清空失败: ${error.message}`)
      })
  }
}

// 切换下载下拉菜单
function toggleDownloadDropdown() {
  isDownloadDropdownOpen.value = !isDownloadDropdownOpen.value
}

// 下载访谈内容
async function downloadContent(format = 'excel') {
  if (format !== 'excel') {
    alert('目前仅支持Excel格式导出');
    isDownloadDropdownOpen.value = false;
    return;
  }

  try {
    // 生成默认文件名
    const defaultName = `项目访谈汇总_${projectName.value}_${new Date().toISOString().slice(0, 10)}.xlsx`;
    
    // 调用 apiService 的正确方法，对应后端 /api/export/project/{id} 接口
    await apiService.exportAllSessions(projectId, defaultName);
    
    // 提示（可选，因为 apiService 已经会触发下载）
    console.log('导出请求已发送');
  } catch (error) {
    console.error('导出失败:', error);
    alert('导出失败，请重试');
  } finally {
    isDownloadDropdownOpen.value = false;
  }
}

// 显示上一份访谈记录
function showPreviousInterview() {
  const currentIndex = interviews.value.findIndex(item => item.id === currentDialogId.value)
  if (currentIndex > 0) {
    const previousInterview = interviews.value[currentIndex - 1]
    currentInterview.value = previousInterview
    currentDialogId.value = previousInterview.id
    currentDialog.value = previousInterview.transcript || []
    participantName.value = previousInterview.interviewee_info?.name || '匿名用户'
    participantInfo.value = previousInterview.interviewee_info?.info || ''
  }
}

// 显示下一份访谈记录
function showNextInterview() {
  const currentIndex = interviews.value.findIndex(item => item.id === currentDialogId.value)
  if (currentIndex < interviews.value.length - 1) {
    const nextInterview = interviews.value[currentIndex + 1]
    currentInterview.value = nextInterview
    currentDialogId.value = nextInterview.id
    currentDialog.value = nextInterview.transcript || []
    participantName.value = nextInterview.interviewee_info?.name || '匿名用户'
    participantInfo.value = nextInterview.interviewee_info?.info || ''
  }
}



// 打开备注弹窗
function openNoteModal(id) {
  currentNoteId.value = id
  // 查找对应的访谈
  const interview = interviews.value.find(item => item.id === id)
  if (interview) {
    // 设置当前备注内容
    currentNoteContent.value = interview.note || ''
    // 显示备注弹窗
    isNoteModalVisible.value = true
  }
}

// 关闭备注弹窗
function closeNoteModal() {
  isNoteModalVisible.value = false
  // 清空当前备注ID和内容
  currentNoteId.value = null
  currentNoteContent.value = ''
}

// 保存备注
function saveNote() {
  if (currentNoteId.value) {
    // 查找对应的访谈
    const interview = interviews.value.find(item => item.id === currentNoteId.value)
    if (interview) {
      // 更新本地备注
      interview.note = currentNoteContent.value
      // 调用API保存备注
      apiService.put(`/sessions/${currentNoteId.value}/note`, { note: currentNoteContent.value })
        .then(() => {
          alert('备注保存成功')
          closeNoteModal()
        })
        .catch(error => {
          console.error('保存备注失败:', error)
          alert(`保存备注失败: ${error.message}`)
        })
    }
  }
}

// 切换星标状态
async function toggleStar(id) {
  const interview = interviews.value.find(item => item.id === id)
  if (interview) {
    interview.is_starred = !interview.is_starred
    try {
      await apiService.put(`/sessions/${id}/star`, { is_starred: interview.is_starred })
    } catch (error) {
      console.error('更新星标状态失败:', error)
      interview.is_starred = !interview.is_starred // 恢复原状态
    }
  }
}

// 删除访谈
async function deleteInterview(id) {
  if (confirm('确定要删除这条内容吗？')) {
    if (confirm('再次确认删除？')) {
      try {
        await apiService.delete(`/sessions/${id}`)
        interviews.value = interviews.value.filter(item => item.id !== id)
        updateStats()
      } catch (error) {
        console.error('删除失败:', error)
        alert(`删除失败: ${error.message}`)
      }
    }
  }
}

// 跳转到指定页码
function goToPage(page) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  jumpPage.value = page
  // 这里可以添加重新加载数据的逻辑
}

// 改变每页显示数量
function changePageSize() {
  currentPage.value = 1
  jumpPage.value = 1
  totalPages.value = Math.ceil(totalInterviews.value / pageSize.value)
  // 这里可以添加重新加载数据的逻辑
}

// 组件挂载时初始化
onMounted(() => {
  fetchInterviews()
  
  // 设置定时器，每5秒自动刷新一次数据
  const refreshInterval = setInterval(() => {
    fetchInterviews()
  }, 30000)
  
  // 组件卸载时清除定时器
  onUnmounted(() => {
    clearInterval(refreshInterval)
  })
})
</script>

<style scoped>
.status-indicator {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 6px;
}
.status-running {
  background-color: #10b981;
}
.table-container {
  overflow-x: auto;
}
th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}
th {
  background-color: #f9fafb;
  font-weight: 600;
  font-size: 14px;
  color: #374151;
}
td {
  font-size: 14px;
  color: #6b7280;
}
.stat-badge {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 14px;
  font-weight: 600;
  margin-left: 8px;
}
.action-btn {
  padding: 4px 8px;
  border: none;
  background: none;
  cursor: pointer;
  color: #6b7280;
  border-radius: 4px;
  transition: all 0.2s;
}
.action-btn:hover {
  background-color: #f3f4f6;
  color: #374151;
}
.pagination-btn {
  padding: 6px 12px;
  border: 1px solid #e5e7eb;
  background-color: white;
  cursor: pointer;
  border-radius: 4px;
  margin: 0 2px;
  transition: all 0.2s;
}
.pagination-btn:hover {
  background-color: #f3f4f6;
}
.pagination-btn.active {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}
</style>
