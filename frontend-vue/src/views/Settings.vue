<!-- eslint-disable vue/multi-word-component-names -->
<template>
        <div class="mb-8">
            <h2 class="text-2xl font-bold text-gray-800">系统设置</h2>
            <p class="text-gray-500 mt-1 text-sm">管理您的账户偏好和应用选项</p>
        </div>

        <div class="space-y-6">
            <!-- 通用设置 -->
            <section class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <div class="px-6 py-4 border-b border-gray-100">
                    <h3 class="font-bold text-gray-700 flex items-center gap-2">
                        <i class="fas fa-wifi text-blue-500"></i> 通用设置
                    </h3>
                </div>
                
                <div class="divide-y divide-gray-100">
                    <!-- 通知 -->
                    <div class="setting-item p-5 flex items-center justify-between">
                        <div class="flex items-center gap-4">
                            <div class="w-10 h-10 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center">
                                <i class="fas fa-bell"></i>
                            </div>
                            <div>
                                <p class="font-medium text-gray-800">消息通知</p>
                                <p class="text-xs text-gray-500">接收访谈进度和状态更新</p>
                            </div>
                        </div>
                        <label class="relative inline-flex items-center cursor-pointer">
                            <input v-model="notifyEnabled" type="checkbox" class="sr-only peer" @change="toggleNotify">
                            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                        </label>
                    </div>

                    <!-- 缓存 -->
                    <div class="setting-item p-5 flex items-center justify-between cursor-pointer" @click="clearCache">
                        <div class="flex items-center gap-4">
                            <div class="w-10 h-10 bg-orange-50 text-orange-500 rounded-full flex items-center justify-center">
                                <i class="fas fa-broom"></i>
                            </div>
                            <div>
                                <p class="font-medium text-gray-800">清理缓存</p>
                                <p class="text-xs text-gray-500">释放本地存储空间</p>
                            </div>
                        </div>
                        <div class="flex items-center gap-2">
                            <span id="cache-size" class="text-sm text-gray-400">{{ cacheSize }}</span>
                            <i class="fas fa-chevron-right text-gray-300 text-xs"></i>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 账户与安全 -->
            <section class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <div class="px-6 py-4 border-b border-gray-100">
                    <h3 class="font-bold text-gray-700 flex items-center gap-2">
                        <i class="fas fa-shield-alt text-green-600"></i> 账户与安全
                    </h3>
                </div>
                
                <div class="divide-y divide-gray-100">
                    <div class="setting-item p-5 flex items-center justify-between cursor-pointer" @click="navigateToProfile">
                        <div class="flex items-center gap-4">
                            <div class="w-10 h-10 bg-green-50 text-green-600 rounded-full flex items-center justify-center">
                                <i class="fas fa-user-edit"></i>
                            </div>
                            <div>
                                <p class="font-medium text-gray-800">个人资料</p>
                                <p class="text-xs text-gray-500">修改用户名、邮箱和密码</p>
                            </div>
                        </div>
                        <i class="fas fa-chevron-right text-gray-300 text-xs"></i>
                    </div>

                    <div class="setting-item p-5 flex items-center justify-between cursor-pointer" @click="navigateToPrivacy">
                        <div class="flex items-center gap-4">
                            <div class="w-10 h-10 bg-purple-50 text-purple-600 rounded-full flex items-center justify-center">
                                <i class="fas fa-lock"></i>
                            </div>
                            <div>
                                <p class="font-medium text-gray-800">隐私政策</p>
                                <p class="text-xs text-gray-500">查看数据使用协议</p>
                            </div>
                        </div>
                        <i class="fas fa-chevron-right text-gray-300 text-xs"></i>
                    </div>
                </div>
            </section>

            <!-- 退出登录区 -->
            <section>
                <button @click="openLogoutModal" class="w-full bg-white border border-red-100 text-red-500 font-bold py-4 rounded-2xl shadow-sm hover:bg-red-50 hover:border-red-200 transition-all flex items-center justify-center gap-2">
                    <i class="fas fa-sign-out-alt"></i> 退出登录
                </button>
                <p class="text-center text-xs text-gray-400 mt-4">AI Interview Agent v1.0.0</p>
            </section>
        </div>

    <!-- 退出确认弹窗 -->
    <div id="logout-modal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" v-show="showLogoutModal">
        <div class="bg-white rounded-2xl p-6 w-full max-w-sm shadow-2xl transform transition-all scale-100">
            <div class="text-center">
                <div class="w-14 h-14 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4 text-danger text-2xl">
                    <i class="fas fa-power-off"></i>
                </div>
                <h3 class="text-lg font-bold text-gray-900 mb-2">确认退出？</h3>
                <p class="text-sm text-gray-500 mb-6">退出后需要重新登录才能管理您的项目。</p>
                <div class="flex gap-3">
                    <button @click="closeLogoutModal" class="flex-1 py-2.5 border border-gray-300 rounded-xl text-gray-600 font-medium hover:bg-gray-50">取消</button>
                    <button @click="handleLogout" class="flex-1 py-2.5 bg-danger text-white rounded-xl font-medium hover:bg-red-600">退出</button>
                </div>
            </div>
        </div>
    </div>

    <!-- 提示 Toast -->
    <div id="toast" class="fixed top-24 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white px-6 py-3 rounded-lg shadow-xl z-50 transition-opacity duration-300 opacity-0 pointer-events-none flex items-center gap-2">
        <i class="fas fa-check-circle text-green-400"></i>
        <span id="toast-msg">{{ toastMessage }}</span>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import useUserStore from '../store/user';

const router = useRouter();
const userStore = useUserStore();

// 响应式数据
const username = ref('');
const notifyEnabled = ref(true);
const cacheSize = ref('12.5 MB');
const showLogoutModal = ref(false);
const toastMessage = ref('');
const toastTimeout = ref(null);

// 显示Toast消息
function showToast(msg) {
  toastMessage.value = msg;
  const toast = document.getElementById('toast');
  toast.classList.remove('opacity-0');
  
  if (toastTimeout.value) {
    clearTimeout(toastTimeout.value);
  }
  
  toastTimeout.value = setTimeout(() => {
    toast.classList.add('opacity-0');
  }, 2000);
}

// 切换通知状态
function toggleNotify() {
  showToast(notifyEnabled.value ? '通知已开启' : '通知已关闭');
}

// 清理缓存
function clearCache() {
  // 显示加载状态
  const cacheSizeElement = document.getElementById('cache-size');
  cacheSizeElement.innerHTML = '<i class="fas fa-circle-notch fa-spin text-gray-400"></i>';
  
  setTimeout(() => {
    // 清理本地存储
    localStorage.clear();
    sessionStorage.clear();
    
    // 更新缓存大小
    cacheSize.value = '0 MB';
    cacheSizeElement.textContent = '0 MB';
    
    showToast('缓存清理完成');
    
    // 3秒后重置显示
    setTimeout(() => {
      cacheSize.value = '12.5 MB';
      cacheSizeElement.textContent = '12.5 MB';
    }, 3000);
  }, 800);
}

// 个人资料导航
function navigateToProfile() {
  // 这里可以跳转到个人资料页面
  showToast('个人资料页面开发中');
}

// 隐私政策导航
function navigateToPrivacy() {
  // 这里可以跳转到隐私政策页面
  showToast('隐私政策页面开发中');
}

// 打开退出模态框
function openLogoutModal() {
  showLogoutModal.value = true;
}

// 关闭退出模态框
function closeLogoutModal() {
  showLogoutModal.value = false;
}

// 处理退出登录
function handleLogout() {
  userStore.logout();
  router.push('/login');
}

// 初始化
onMounted(() => {
  // 获取用户名
  const user = userStore.username;
  if (user) {
    username.value = user;
  }
  
  // 初始化缓存大小
  cacheSize.value = '12.5 MB';
});
</script>

<style scoped>
.setting-item {
  transition: background-color 0.2s ease;
}

.setting-item:hover {
  background-color: #f8fafc;
}
</style>