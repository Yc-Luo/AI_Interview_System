<template>
  <!-- 根据路由元信息动态选择布局 -->
  <template v-if="$route.meta.layout === 'main'">
    <div class="min-h-screen bg-bg-light font-sans flex flex-col">
      <!-- 顶部导航栏 -->
      <header class="bg-white border-b border-border-light px-6 py-4 sticky top-0 z-50">
        <div class="max-w-5xl mx-auto flex justify-between items-center">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-white font-bold">AI</div>
            <h1 class="text-xl font-bold text-gray-800">AI访谈智能体</h1>
          </div>
          
          <div class="flex items-center space-x-6">
            <!-- 导航链接 -->
            <nav class="flex space-x-6 text-sm font-medium text-gray-600">
              <router-link to="/home" class="hover:text-primary transition-colors" :class="{ 'text-primary': $route.path === '/home' }">工作台</router-link>
              <router-link to="/outline-list" class="hover:text-primary transition-colors" :class="{ 'text-primary': $route.path === '/outline-list' }">我的提纲</router-link>
              <router-link to="/interview-list" class="hover:text-primary transition-colors" :class="{ 'text-primary': $route.path === '/interview-list' }">访谈数据</router-link>
            </nav>

            <div class="h-6 w-px bg-gray-200 hidden md:block"></div>

            <!-- 设置按钮 -->
            <div class="flex items-center gap-3">
              <span id="username-display" class="text-sm font-bold text-gray-800 hidden sm:block">{{ username }}</span>
              <button @click="$router.push('/settings')" class="w-9 h-9 rounded-full bg-gray-100 hover:bg-gray-200 hover:text-primary flex items-center justify-center transition-colors" title="设置">
                <i class="fas fa-cog"></i>
              </button>
            </div>
          </div>
        </div>
      </header>

      <!-- 主要内容区域 -->
      <main class="max-w-5xl mx-auto px-6 py-8 w-full flex-1">
        <router-view />
      </main>

      <!-- 页脚 -->
      <footer class="bg-white border-t mt-auto py-6">
        <div class="max-w-5xl mx-auto px-6 text-center text-sm text-gray-500">
          <p>AI访谈智能体 &copy; {{ new Date().getFullYear() }}</p>
        </div>
      </footer>
    </div>
  </template>
  <template v-else>
    <router-view />
  </template>
</template>

<script setup>
import { computed } from 'vue';
import useUserStore from './store/user';

const userStore = useUserStore();
const username = computed(() => userStore.username || '用户');
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  -webkit-tap-highlight-color: transparent;
  background-color: #f9fafb;
}

#app {
  width: 100%;
  min-height: 100vh;
}

/* 自定义CSS变量 */
:root {
  --primary: #2563eb;
  --secondary: #6b7280;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --bg-light: #f9fafb;
  --border-light: #e5e7eb;
}

/* 全局颜色类 */
.bg-primary {
  background-color: var(--primary);
}

.text-primary {
  color: var(--primary);
}

.border-primary {
  border-color: var(--primary);
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}
</style>
