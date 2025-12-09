<template>
    <!-- 标题与统计 -->
    <div class="flex flex-col md:flex-row justify-between items-end mb-8 gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-800">我的访谈项目</h2>
        <p class="text-gray-500 mt-1 text-sm">监控项目进度，管理回收数据</p>
      </div>
      
      <div class="flex gap-4">
        <div class="bg-white px-4 py-2 rounded-xl border border-gray-200 shadow-sm text-center min-w-[80px]">
          <p class="text-xs text-gray-500">总项目</p>
          <p class="text-xl font-bold text-primary">{{ totalProjects }}</p>
        </div>
        <div class="bg-white px-4 py-2 rounded-xl border border-gray-200 shadow-sm text-center min-w-[80px]">
          <p class="text-xs text-gray-500">进行中</p>
          <p class="text-xl font-bold text-success">{{ activeProjects }}</p>
        </div>
        <div class="bg-white px-4 py-2 rounded-xl border border-gray-200 shadow-sm text-center min-w-[80px]">
          <p class="text-xs text-gray-500">已结束</p>
          <p class="text-xl font-bold text-gray-400">{{ completedProjects }}</p>
        </div>
      </div>
    </div>

    <!-- 筛选工具栏 -->
    <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-200 mb-6 flex flex-col md:flex-row gap-4 items-center justify-between">
      <div class="relative w-full md:w-96">
        <i class="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索项目名称..."
          class="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-primary"
        >
      </div>
      
      <div class="flex gap-2 w-full md:w-auto">
        <select
          v-model="statusFilter"
          class="px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-600 focus:outline-none cursor-pointer"
        >
          <option value="all">全部状态</option>
          <option value="active">进行中</option>
          <option value="completed">已结束</option>
        </select>
        <router-link
          to="/outline-list"
          class="bg-primary hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-bold transition-colors whitespace-nowrap"
        >
          <i class="fas fa-plus mr-1"></i> 新发起
        </router-link>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" id="project-list" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
      <div class="h-40 bg-gray-200 rounded-2xl animate-pulse"></div>
      <div class="h-40 bg-gray-200 rounded-2xl animate-pulse"></div>
    </div>

    <!-- 项目列表 -->
    <div v-else-if="filteredProjects.length > 0" id="project-list" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
      <div
              v-for="p in filteredProjects"
              :key="p.id"
              class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 card-hover cursor-pointer relative group"
              @click="goToProject($event, p.id)"
            >
        <div class="flex justify-between items-start mb-4">
          <div class="flex items-start gap-4 flex-1 min-w-0">
            <div class="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center flex-shrink-0">
              <i class="fas fa-clipboard-list text-xl"></i>
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="text-lg font-bold text-gray-800 group-hover:text-primary transition-colors truncate">{{ p.outline_title || '未命名项目' }}</h3>
              <p class="text-xs text-gray-400 mt-1">ID: {{ p.id.substring(0,8) }}...</p>
            </div>
          </div>
          <span :class="['status-badge', statusConfig[p.status]?.class || 'bg-gray-100 text-gray-600']" class="flex items-center gap-1 ml-2 flex-shrink-0">
            <i :class="['fas', statusConfig[p.status]?.icon || 'fa-circle']" class="text-[10px]"></i> {{ statusConfig[p.status]?.label || p.status }}
          </span>
        </div>
        
        <div class="flex items-center gap-6 mb-4 text-sm text-gray-600">
          <div class="flex items-center gap-2">
            <i class="fas fa-users text-gray-400"></i>
            <span class="font-bold">{{ p.session_count || 0 }}</span> 份记录
          </div>
          <div class="flex items-center gap-2">
            <i class="far fa-calendar-alt text-gray-400"></i>
            <span>{{ formatDate(p.created_at) }}</span>
          </div>
        </div>

        <div class="border-t border-gray-100 pt-4 flex justify-between items-center">
          <div class="flex gap-2">
            <button @click.stop="openShareModal(p.id)" class="text-sm text-primary font-bold hover:bg-blue-50 px-3 py-1.5 rounded-lg transition-colors">
              <i class="fas fa-share-alt mr-1"></i> 分享链接
            </button>
            <router-link :to="`/outline-edit?outlineId=${p.outline_id}&projectId=${p.id}`" class="text-sm text-primary font-bold hover:bg-blue-50 px-3 py-1.5 rounded-lg transition-colors">
              <i class="fas fa-edit mr-1"></i> 提纲修改
            </router-link>
            <router-link :to="`/ai-config?outlineId=${p.outline_id}&projectId=${p.id}`" class="text-sm text-primary font-bold hover:bg-blue-50 px-3 py-1.5 rounded-lg transition-colors">
              <i class="fas fa-robot mr-1"></i> AI配置
            </router-link>
          </div>
          <!-- 状态操作下拉菜单 -->
          <div class="relative">
            <button @click.stop="toggleStatusMenu($event, `menu-${p.id}`)" class="text-gray-400 hover:text-gray-600 px-2 js-menu-toggle-btn">
              <i class="fas fa-ellipsis-h"></i>
            </button>
            <div :id="`menu-${p.id}`" class="absolute right-0 bottom-full mb-2 w-48 bg-white rounded-xl shadow-lg border border-gray-100 py-2 z-50" v-show="openMenuId === `menu-${p.id}`">
              <button
                v-if="p.status !== 'active'"
                @click.stop="updateProjectStatus($event, p.id, 'active')"
                class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <i class="fas fa-play-circle text-success mr-2"></i> 开始项目
              </button>
              <button
                v-if="p.status !== 'paused'"
                @click.stop="updateProjectStatus($event, p.id, 'paused')"
                class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <i class="fas fa-pause-circle text-yellow-500 mr-2"></i> 暂停项目
              </button>
              <button
                v-if="p.status !== 'completed'"
                @click.stop="updateProjectStatus($event, p.id, 'completed')"
                class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <i class="fas fa-check-circle text-gray-500 mr-2"></i> 结束项目
              </button>
              <div class="border-t border-gray-100 my-1"></div>
              <button @click.stop="deleteProject($event, p.id)" class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-50 transition-colors">
                <i class="fas fa-trash text-red-500 mr-2"></i> 删除项目
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else id="empty-state" class="flex flex-col items-center justify-center py-20 text-center">
      <div class="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mb-4 text-gray-400 text-3xl">
        <i class="fas fa-folder-open"></i>
      </div>
      <h3 class="text-lg font-bold text-gray-700">暂无访谈项目</h3>
      <p class="text-gray-500 text-sm mt-1 mb-6">您还没有发布任何访谈，请前往提纲页发起。</p>
      <router-link to="/outline-list" class="text-primary font-bold hover:underline">去创建提纲</router-link>
    </div>

    <!-- 分享弹窗 -->
    <div id="share-modal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" v-show="showShareModal">
      <div class="bg-white rounded-2xl p-6 w-full max-w-sm shadow-2xl">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-gray-800">分享访谈链接</h3>
          <button @click="closeShareModal" class="text-gray-400 hover:text-gray-600"><i class="fas fa-times"></i></button>
        </div>
        <div class="bg-gray-50 p-3 rounded-lg border border-gray-200 mb-4">
          <p id="share-link-text" class="text-xs text-gray-600 break-all font-mono">{{ shareLink }}</p>
        </div>
        <button @click="copyShareLink" class="w-full bg-primary text-white py-2.5 rounded-xl font-bold hover:bg-blue-700 transition-colors">
          <i class="fas fa-copy mr-2"></i>复制链接
        </button>
      </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiService from '../services/api';

const router = useRouter();

// 状态管理
const projectsData = ref([]);
const loading = ref(true);
const searchQuery = ref('');
const statusFilter = ref('all');
const openMenuId = ref(null);
const showShareModal = ref(false);
const shareLink = ref('');

// 用户名已移除，由MainLayout提供

// 状态配置
const statusConfig = {
  'active': { label: '进行中', class: 'status-active', icon: 'fa-circle-play' },
  'paused': { label: '已暂停', class: 'status-paused', icon: 'fa-pause-circle' },
  'completed': { label: '已结束', class: 'status-completed', icon: 'fa-check-circle' }
};

// 统计数据
const totalProjects = computed(() => projectsData.value.length);
const activeProjects = computed(() => projectsData.value.filter(p => p.status === 'active').length);
const completedProjects = computed(() => projectsData.value.filter(p => p.status === 'completed').length);

// 筛选后的项目
const filteredProjects = computed(() => {
  return projectsData.value.filter(p => {
    const matchSearch = (p.outline_title || '未命名项目').toLowerCase().includes(searchQuery.value.toLowerCase());
    const matchFilter = statusFilter.value === 'all' || p.status === statusFilter.value;
    return matchSearch && matchFilter;
  });
});

// 格式化日期
function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString();
}

// 跳转到访谈项目详情页
function goToProject(event, projectId) {
  // 如果点击的是按钮或链接元素，不执行跳转
  if (event.target.closest('button') || event.target.closest('a')) {
    return;
  }
  router.push(`/interview-detail?projectId=${projectId}`);
}

// 切换状态菜单，与HTML版本保持一致
function toggleStatusMenu(event, menuId) {
  event.stopPropagation();
  
  // 切换当前菜单
  if (openMenuId.value === menuId) {
    openMenuId.value = null;
  } else {
    openMenuId.value = menuId;
  }
}

// 关闭所有菜单
function closeAllMenus() {
  openMenuId.value = null;
}

// 分享功能
function openShareModal(projectId) {
  const link = `${window.location.origin}/guest-interview?projectId=${projectId}`;
  shareLink.value = link;
  showShareModal.value = true;
}

function closeShareModal() {
  showShareModal.value = false;
}

async function copyShareLink() {
  try {
    await navigator.clipboard.writeText(shareLink.value);
    alert("链接已复制！");
    closeShareModal();
  } catch (error) {
    console.error('复制失败:', error);
    alert("复制失败，请手动复制");
  }
}

// 更新项目状态，与HTML版本保持一致
async function updateProjectStatus(event, projectId, newStatus) {
  event.stopPropagation();
  
  try {
    await apiService.put(`/projects/${projectId}`, { status: newStatus });
    await fetchProjects();
    closeAllMenus();
    alert('项目状态已更新');
  } catch (error) {
    console.error('更新项目状态失败:', error);
    alert(`状态更新失败: ${error.message}`);
  }
}

// 删除项目，与HTML版本保持一致
async function deleteProject(event, projectId) {
  event.stopPropagation();
  
  if (!confirm('确定要删除这个项目吗？此操作不可恢复！')) {
    return;
  }
  
  try {
    await apiService.delete(`/projects/${projectId}`);
    await fetchProjects();
    closeAllMenus();
    alert('项目已删除');
  } catch (error) {
    console.error('删除项目失败:', error);
    alert(`删除项目失败: ${error.message}`);
  }
}

// 获取项目数据
async function fetchProjects() {
  loading.value = true;
  try {
    // 获取项目列表
    const response = await apiService.get('/projects/');
    const projects = response.items || [];
    
    // 确保每个项目都有session_count字段
    projectsData.value = projects.map(project => ({
      ...project,
      session_count: project.session_count || 0
    }));
    
    // 获取所有会话数据，用于计算每个项目的记录数量
    const sessionsResponse = await apiService.get('/sessions');
    const allSessions = sessionsResponse.items || [];
    
    // 统计每个项目的会话数量
    projectsData.value.forEach(project => {
      const sessionCount = allSessions.filter(session => session.project_id === project.id).length;
      project.session_count = sessionCount;
    });
  } catch (e) {
    console.error('获取项目数据失败:', e);
    alert(`数据加载失败：${e.message}`);
  } finally {
    loading.value = false;
  }
}

// 初始化
onMounted(async () => {
  await fetchProjects();
  
  // 添加智能自动刷新功能
  let autoRefreshEnabled = true;
  let lastUserActivity = Date.now();
  const USER_INACTIVE_THRESHOLD = 30000; // 30秒无活动后自动刷新
  const REFRESH_INTERVAL = 30000; // 刷新间隔
  
  // 检测用户活动
  const userActivityEvents = ['click', 'keydown', 'scroll', 'mousemove'];
  userActivityEvents.forEach(event => {
    document.addEventListener(event, () => {
      lastUserActivity = Date.now();
      autoRefreshEnabled = true;
    });
  });
  
  // 使用Page Visibility API检测页面可见性
  document.addEventListener('visibilitychange', () => {
    autoRefreshEnabled = !document.hidden;
  });
  
  // 定时刷新函数
  const autoRefresh = async () => {
    const now = Date.now();
    // 只有在页面可见且用户无活动超过阈值时才刷新
    if (autoRefreshEnabled && now - lastUserActivity > USER_INACTIVE_THRESHOLD) {
      await fetchProjects();
    }
    // 继续下一次刷新
    setTimeout(autoRefresh, REFRESH_INTERVAL);
  };
  
  // 启动自动刷新
  setTimeout(autoRefresh, REFRESH_INTERVAL);
});

// 点击外部关闭菜单
onMounted(() => {
  document.addEventListener('click', (e) => {
    if (!e.target.closest('[id^="menu-"]') && !e.target.closest('.js-menu-toggle-btn')) {
      closeAllMenus();
    }
  });
});
</script>

<style scoped>
.card-hover {
  transition: all 0.2s ease-in-out;
}

.card-hover:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.status-badge {
  @apply px-2.5 py-0.5 rounded-full text-xs font-medium;
}

.status-active {
  @apply bg-green-100 text-green-800;
}

.status-paused {
  @apply bg-yellow-100 text-yellow-800;
}

.status-completed {
  @apply bg-gray-100 text-gray-800;
}
</style>