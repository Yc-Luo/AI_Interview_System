<template>
  <div class="bg-bg h-screen overflow-hidden flex flex-col text-gray-800">
    <!-- 等待/准备页 -->
    <div id="page-waiting" v-if="interviewStore.currentPage === 'waiting'" class="flex-1 flex flex-col h-full bg-white relative z-30 transition-transform duration-500">
      <!-- 顶部背景装饰 -->
      <div class="h-48 bg-gradient-to-b from-blue-50 to-white w-full absolute top-0 left-0 z-0"></div>

      <div class="flex-1 flex flex-col z-10 px-6 pt-12 pb-6 overflow-y-auto no-scrollbar">
        <!-- 项目 Logo/名称 -->
        <div class="text-center mb-8 animate-fade-in">
          <div class="w-16 h-16 bg-white rounded-2xl shadow-md flex items-center justify-center mx-auto mb-4 text-primary text-3xl border border-gray-100">
            <i class="fas fa-university"></i>
          </div>
          <h1 class="text-2xl font-bold text-gray-900 mb-1">{{ interviewStore.projectInfo?.outline_title || '大学生职业规划调研' }}</h1>
        </div>

        <!-- AI 形象卡片 -->
        <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 mb-6 animate-slide-up" style="animation-delay: 0.1s;">
          <div class="flex items-center gap-4 mb-4">
            <div class="w-14 h-14 rounded-full bg-blue-100 flex items-center justify-center text-2xl relative">
              <!-- 图标替换：使用 FontAwesome -->
              <i :class="aiIconClass" class="text-primary"></i>
              <div class="absolute bottom-0 right-0 w-4 h-4 bg-green-500 border-2 border-white rounded-full"></div>
            </div>
            <div>
              <h3 class="font-bold text-lg">AI 访谈助手·{{ interviewStore.aiConfig?.name || '李教授' }}</h3>
              <p class="text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full inline-block mt-1">{{ interviewStore.aiConfig?.role_settings?.tone || '专业严谨' }}</p>
            </div>
          </div>
          <div class="bg-gray-50 rounded-xl p-3 relative">
            <div class="absolute -top-1 left-6 w-3 h-3 bg-gray-50 transform rotate-45 border-l border-t border-gray-100"></div>
            <p class="text-sm text-gray-600 leading-relaxed">
              {{ interviewStore.aiConfig?.role_settings?.opening_text || '您好！我是本次研究设定的AI访谈助理。稍后我将根据提纲与您进行约 15 分钟的交流。请放松心情，就像平时聊天一样。' }}
            </p>
          </div>
        </div>

        <!-- 访谈说明 -->
        <div class="space-y-4 animate-slide-up" style="animation-delay: 0.2s;">
          <div class="flex items-start gap-3">
            <div class="w-8 h-8 rounded-full bg-green-50 text-green-600 flex items-center justify-center flex-shrink-0 mt-0.5">
              <i class="fas fa-shield-alt text-sm"></i>
            </div>
            <div>
              <h4 class="font-bold text-sm">隐私保护</h4>
              <p class="text-xs text-gray-500 mt-0.5">您的回答仅用于学术研究分析，所有个人信息将严格保密，不会对外公开。</p>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <div class="w-8 h-8 rounded-full bg-orange-50 text-orange-600 flex items-center justify-center flex-shrink-0 mt-0.5">
              <i class="fas fa-volume-up text-sm"></i>
            </div>
            <div>
              <h4 class="font-bold text-sm">环境要求</h4>
              <p class="text-xs text-gray-500 mt-0.5">请确保您处于相对安静的环境中，以便 AI 能清晰识别您的语音。</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部操作区 -->
      <div class="p-4 pb-8 bg-white border-t border-gray-100 z-10">
        <!-- 麦克风检测状态 -->
        <div id="mic-check-status" class="flex items-center justify-center gap-2 mb-3 text-sm text-gray-500 transition-all">
          <i class="fas fa-microphone-slash"></i> 麦克风权限未检测
        </div>

        <button 
          id="btn-start-check" 
          class="w-full bg-primary text-white rounded-xl py-3.5 font-bold text-lg shadow-lg shadow-blue-200 active:scale-95 transition-all flex items-center justify-center gap-2"
          @click="startMicCheck"
          :disabled="isLoading"
        >
          <i v-if="isLoading && loadingText.includes('连接访谈服务器')" class="fas fa-circle-notch fa-spin"></i>
          <i v-else-if="isLoading && loadingText.includes('检测环境噪音')" class="fas fa-microphone"></i>
          <i v-else-if="isLoading && loadingText.includes('检测通过')" class="fas fa-check"></i>
          {{ isLoading ? loadingText : '开始检测并进入' }}
        </button>
      </div>
    </div>
    
    <!-- 访谈进行页 -->
    <div id="page-interview" v-else-if="interviewStore.currentPage === 'interview'" class="fixed inset-0 bg-gray-50 z-20 flex flex-col">
      
      <!-- 顶部导航 -->
      <header class="bg-white px-4 py-3 flex justify-between items-center shadow-sm z-20">
        <!-- 左侧：AI教授信息 -->
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-sm">
            <i :class="aiIconClass" class="text-primary"></i>
          </div>
          <div class="flex flex-col">
            <span class="text-sm font-bold text-gray-800">AI {{ interviewStore.aiConfig?.name || '李教授' }}</span>
            <span class="text-[10px] text-green-600 flex items-center gap-1">
              <span class="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span> 已连接到AI访谈助手
            </span>
          </div>
        </div>
        
        <!-- 中间：访谈时间信息 -->
        <div class="flex flex-col items-center">
          <span class="text-[10px] text-gray-500">访谈开始 - </span>
          <span class="text-[10px] text-gray-500">{{ interviewTime }}</span>
        </div>
        
        <!-- 右侧：功能按钮 -->
        <div class="flex items-center gap-4">
          <!-- 语音聊天切换按钮 -->
          <button 
            id="voice-toggle-btn"
            @click="toggleVoiceChatMode" 
            :class="['px-2 py-1 transition-colors flex items-center gap-1', isAIVoiceEnabled ? 'text-primary' : 'text-gray-400 hover:text-primary']"
          >
            <i class="fas fa-phone text-lg"></i>
          </button>
          <!-- 电源按钮（结束访谈） -->
          <button @click="openTerminateModal" class="text-gray-400 hover:text-red-500 px-2 py-1 transition-colors">
            <i class="fas fa-power-off text-lg"></i>
          </button>
        </div>
      </header>

      <!-- 聊天区域 -->
      <main id="chat-container" class="flex-1 overflow-y-auto p-4 space-y-6 no-scrollbar pb-32">
        <!-- 历史记录占位 -->
        <div id="interview-start-time" class="text-center text-xs text-gray-400 my-4">访谈开始 - {{ interviewTime }}</div>
        
        <!-- 聊天消息 -->
        <div v-for="(message, index) in interviewStore.messages" :key="index" class="flex gap-3 animate-fade-in" :class="message.type === 'user' ? 'flex-row-reverse' : ''">
          <div v-if="message.type === 'user'" class="w-8 h-8 rounded-full bg-blue-600 flex-shrink-0 flex items-center justify-center mt-1 text-white text-xs">我</div>
          <div v-else class="w-8 h-8 rounded-full bg-blue-100 flex-shrink-0 flex items-center justify-center mt-1">
            <i :class="aiIconClass" class="text-primary text-xs"></i>
          </div>
          <div :class="['chat-bubble', message.type === 'user' ? 'user' : 'ai']">
            <div v-if="message.type === 'system'" class="text-xs text-gray-500">
              {{ message.content }}
            </div>
            <div v-else-if="message.type === 'user' && message.isVoice" class="flex items-center gap-2">
              <i class="fas fa-wifi rotate-90"></i> {{ message.content }}
            </div>
            <div v-else>
              {{ message.content }}
            </div>
          </div>
        </div>
        
        <!-- 加载中消息 -->
        <div v-if="isLoading" id="ai-loading" class="flex gap-3 animate-fade-in">
          <div class="w-8 h-8 rounded-full bg-blue-100 flex-shrink-0 flex items-center justify-center mt-1">
            <i :class="aiIconClass" class="text-primary text-xs"></i>
          </div>
          <div class="chat-bubble ai text-gray-400">
            <i class="fas fa-circle-notch fa-spin"></i> 思考中...
          </div>
        </div>
      </main>

      <!-- 底部输入控制区 -->
      <footer class="bg-white border-t border-gray-100 p-4 pb-8 absolute bottom-0 w-full z-20 transition-all duration-300" id="input-footer">
        
        <!-- 文字模式 UI (默认显示) -->
        <div id="text-ui" :class="['flex items-center gap-3 w-full h-[48px]', isVoiceMode ? 'hidden' : '']">
          <!-- 切换语音按钮 -->
          <button 
            id="toggle-voice-btn"
            @click="switchToVoiceMode" 
            class="w-12 h-12 bg-gray-50 border border-gray-200 rounded-full flex items-center justify-center text-gray-500 hover:bg-gray-100 transition-colors focus:outline-none focus:ring-0 focus:border-transparent"
          >
            <i class="fas fa-microphone text-lg"></i>
          </button>
          
          <!-- 文本输入框 -->
          <div class="flex-1 relative">
            <textarea 
              id="text-input" 
              rows="1" 
              class="w-full h-12 bg-gray-50 border border-gray-200 rounded-full px-4 py-2.5 text-sm resize-none max-h-24 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="请输入回答..."
              v-model="textInput"
              @keydown.enter.exact="sendMessage"
              @keydown.shift.enter="$event.preventDefault(); textInput += '\n'"
            ></textarea>
          </div>
          
          <!-- 发送文字内容按钮 -->
          <button 
            @click="sendMessage" 
            class="w-12 h-12 bg-blue-500 text-white rounded-full flex items-center justify-center hover:bg-blue-600 transition-colors focus:outline-none focus:ring-0 focus:border-transparent"
          >
            <i class="fas fa-paper-plane text-lg"></i>
          </button>
        </div>
        
        <!-- 语音模式 UI (默认隐藏) -->
        <div id="voice-ui" :class="['flex items-center gap-3 w-full h-[48px]', isVoiceMode ? 'flex' : 'hidden']">
          <!-- 切换文字输入按钮 -->
          <button 
            id="toggle-text-btn"
            @click="switchToTextMode" 
            class="w-12 h-12 bg-gray-50 border border-gray-200 rounded-full flex items-center justify-center text-gray-500 hover:bg-gray-100 transition-colors focus:outline-none focus:ring-0 focus:border-transparent"
          >
            <i class="fas fa-keyboard text-lg"></i>
          </button>
          
          <!-- 语音输入按钮 -->
          <div class="relative flex-1">
            <button 
              id="btn-hold-talk"
              @mousedown="startRecording"
              @mouseup="stopRecording"
              @mouseleave="stopRecording"
              @touchstart.prevent="startRecording"
              @touchend.prevent="stopRecording"
              class="w-full h-12 bg-gray-50 border border-gray-200 text-gray-600 rounded-full flex items-center justify-center gap-2 active:bg-blue-500 active:text-white relative select-none touch-none focus:outline-none focus:ring-0 focus:border-transparent"
            >
              <i class="fas fa-microphone text-lg"></i>
              <span>按住说话</span>
            </button>
          </div>
          
          <!-- 打断AI当前发言按钮 -->
          <button 
            id="interrupt-btn"
            @click="interruptAI" 
            class="w-12 h-12 bg-gray-50 border border-gray-200 rounded-full flex items-center justify-center text-gray-500 hover:bg-gray-100 transition-colors focus:outline-none focus:ring-0 focus:border-transparent"
          >
            <i class="fas fa-circle text-lg"></i>
          </button>
        </div>
      </footer>
    </div>
    
    <!-- 结束/感谢页 -->
    <div id="page-end" v-else-if="interviewStore.currentPage === 'end'" class="fixed inset-0 bg-white z-40 flex flex-col items-center justify-center px-8">
      
      <!-- 上传状态 -->
      <div id="upload-status" :class="{ hidden: uploadComplete }" class="w-full max-w-xs text-center mb-8">
        <div class="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-6 relative">
          <i id="status-icon" :class="uploadIconClass" class="text-3xl text-primary animate-bounce"></i>
          <svg class="absolute top-0 left-0 w-full h-full transform -rotate-90">
            <circle cx="40" cy="40" r="38" stroke="#e2e8f0" stroke-width="4" fill="none"/>
            <circle id="upload-circle" cx="40" cy="40" r="38" stroke="#2563eb" stroke-width="4" fill="none" stroke-dasharray="240" stroke-dashoffset="240" class="transition-all duration-1000"/>
          </svg>
        </div>
        <h2 id="status-title" class="text-xl font-bold text-gray-900 mb-2">{{ uploadTitle }}</h2>
        <p id="status-desc" class="text-sm text-gray-500">{{ uploadDescription }}</p>
      </div>

      <!-- 成功后的内容 (默认隐藏) -->
      <div id="success-content" :class="{ hidden: !uploadComplete }" class="w-full max-w-sm flex flex-col items-center animate-fade-in">
        <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mb-6">
          <i class="fas fa-check text-4xl text-success"></i>
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">感谢参与！</h2>
        
        <div class="bg-gray-50 rounded-xl p-4 text-center mb-8 w-full border border-gray-100">
          <div class="w-10 h-10 rounded-full bg-white mx-auto -mt-4 mb-2 shadow-sm flex items-center justify-center text-lg">
            <!-- 图标替换 -->
            <i class="fas fa-user-tie text-primary"></i>
          </div>
          <p class="text-sm text-gray-600 italic">{{ closingText }}</p>
        </div>

        <!-- 联系方式 -->
        <div class="text-center mb-8">
          <p class="text-xs text-gray-400 uppercase tracking-wider mb-2">研究者联系方式</p>
          <p class="text-sm text-gray-700 font-medium"><i class="far fa-envelope mr-1"></i> ycluo@nenu.edu.cn</p>
        </div>

        <!-- 按钮组 -->
        <div class="w-full space-y-3">
          <button @click="openShareModal" class="w-full py-3 bg-white border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors flex items-center justify-center gap-2">
            <i class="fas fa-share-alt"></i> 分享给同学
          </button>
          <button @click="closeWindow" class="w-full py-3 bg-gray-900 text-white rounded-xl font-medium hover:bg-black transition-colors">
            关闭页面
          </button>
        </div>
      </div>
    </div>
    
    <!-- 模态框 -->
    <div v-if="interviewStore.modalVisible" class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center backdrop-blur-sm p-4">
      <!-- 终止确认模态框 -->
      <div v-if="interviewStore.modalType === 'terminate'" class="bg-white rounded-2xl w-full max-w-xs p-6 text-center shadow-2xl transform scale-95 transition-transform">
        <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <i class="fas fa-exclamation text-red-500 text-xl"></i>
        </div>
        <h3 class="text-lg font-bold text-gray-900 mb-2">确定要结束访谈吗？</h3>
        <p class="text-sm text-gray-500 mb-6">当前进度已保存，但提前结束可能导致数据不完整。</p>
        <div class="flex gap-3">
          <button @click="closeModal" class="flex-1 py-2.5 border border-gray-200 rounded-xl text-gray-600 font-medium">取消</button>
          <button @click="confirmModalAction" class="flex-1 py-2.5 bg-red-500 text-white rounded-xl font-medium">结束</button>
        </div>
      </div>
      
      <!-- 分享链接模态框 -->
      <div v-else-if="interviewStore.modalType === 'share'" class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-gray-900">分享访谈链接</h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600 transition-colors">
            <i class="fas fa-times text-lg"></i>
          </button>
        </div>
        <div class="bg-gray-50 rounded-xl p-4 mb-4">
          <input type="text" id="share-link-input" class="w-full bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm font-mono break-all" readonly :value="shareLink">
        </div>
        <button @click="copyShareLink" class="w-full bg-primary text-white py-3 rounded-xl font-bold hover:bg-blue-700 transition-colors flex items-center justify-center gap-2">
          <i class="fas fa-copy"></i> 复制链接
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed, watch, nextTick } from 'vue'
import { useInterviewStore } from '../store/interview'
import apiService from '../services/api'

// 获取访谈状态管理
const interviewStore = useInterviewStore()

// 响应式数据 - 来自InterviewWaiting组件
const isLoading = ref(false)
const loadingText = ref('连接访谈服务器...')

// 响应式数据 - 来自InterviewRunning组件
const interviewTime = ref('')
const isVoiceMode = ref(false) // 默认文字模式
const isRecording = ref(false)
const textInput = ref('')
const audioStream = ref(null)
const mediaRecorder = ref(null)
const audioChunks = ref([])
const isAIVoiceEnabled = ref(false) // AI语音回复开关，默认关闭
const utterance = ref(null) // 语音合成对象

// 响应式数据 - 来自InterviewEnd组件
const uploadComplete = ref(false)
const uploadTitle = ref('正在保存记录...')
const uploadDescription = ref('请勿关闭页面，数据加密上传中')
const uploadIconClass = ref('fas fa-cloud-upload-alt')

// 响应式数据 - 来自InterviewModal组件
const shareLink = ref(window.location.href)

// 计算属性
const aiIconClass = computed(() => {
  const avatarIconMap = {
    'blue': 'fas fa-user-tie',
    'green': 'fas fa-user-graduate',
    'purple': 'fas fa-robot',
    'orange': 'fas fa-smile'
  }
  return avatarIconMap[interviewStore.aiConfig?.role_settings?.avatar_id] || 'fas fa-user-tie'
})

// 来自InterviewEnd组件的计算属性
const closingText = computed(() => {
  return interviewStore.aiConfig?.role_settings?.closing_text || '您的回答非常有见地！特别是关于实习经历的部分，对我们的研究帮助很大。祝您未来职业发展顺利！'
})

// 监听isVisible变化（来自InterviewEnd组件）
watch(() => interviewStore.currentPage, (newVal) => {
  if (newVal === 'end') {
    startUploadSimulation()
  }
})

// 监听消息变化，当AI发送消息时播放语音
watch(() => interviewStore.messages, (newMessages) => {
  // 如果开启了AI语音，且有新的AI消息，播放语音
  if (isAIVoiceEnabled.value && newMessages.length > 0) {
    const lastMessage = newMessages[newMessages.length - 1]
    if (lastMessage.type === 'ai') {
      speakAIResponse(lastMessage.content)
    }
  }
  // 自动滚动到最新消息
  scrollToBottom()
}, { deep: true })

// 滚动到聊天容器底部
const scrollToBottom = () => {
  nextTick(() => {
    const chatContainer = document.getElementById('chat-container')
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight
    }
  })
}

// AI语音回复函数 - 使用后端文字转语音API
const speakAIResponse = async (text) => {
  try {
    // 停止当前正在播放的语音
    window.speechSynthesis.cancel()
    
    // 根据avatar_id映射到对应的语音角色
    const avatarToVoiceMap = {
      'blue': 'manager',
      'green': 'professor',
      'purple': 'assistant',
      'orange': 'student'
    }
    const avatarId = interviewStore.aiConfig?.role_settings?.avatar_id || 'blue'
    const voice = avatarToVoiceMap[avatarId]
    
    // 调用后端文字转语音API
    const response = await apiService.post('/text-to-speech', {
      text: text,
      language: 'zh-CN',
      voice: voice,
      language_style: interviewStore.aiConfig?.role_settings?.tone || '专业严谨'
    })
    
    // 解析响应数据，确保数据结构正确
    const audioData = response.audio_data
    const audioFormat = response.format || 'wav'
    
    // 播放音频
    if (audioData && audioData.length > 0) {
      // 将base64编码的音频数据转换为Blob
      try {
        const byteCharacters = atob(audioData)
        const byteNumbers = new Array(byteCharacters.length)
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i)
        }
        const byteArray = new Uint8Array(byteNumbers)
        const blob = new Blob([byteArray], { type: `audio/${audioFormat}` })
        
        // 创建音频URL并播放
        const audioUrl = URL.createObjectURL(blob)
        const audio = new Audio(audioUrl)
        audio.play()
        
        // 播放完成后释放资源
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl)
        }
      } catch (decodeError) {
        console.error('音频解码失败:', decodeError)
        // 降级处理：使用浏览器内置语音合成
        fallbackSpeakAIResponse(text)
      }
    } else {
      // 后端返回的音频数据为空，降级处理
      fallbackSpeakAIResponse(text)
    }
  } catch (error) {
    console.error('语音合成失败:', error)
    // 降级处理：使用浏览器内置语音合成
    fallbackSpeakAIResponse(text)
  }
}

// 降级处理：使用浏览器内置语音合成
const fallbackSpeakAIResponse = (text) => {
  try {
    // 创建新的语音合成对象
    utterance.value = new SpeechSynthesisUtterance(text)
    
    // 设置语音参数
    utterance.value.lang = 'zh-CN' // 中文语音
    utterance.value.rate = 1.1 // 语速（0.1-10）
    utterance.value.pitch = 1.1 // 音调（0-2）
    utterance.value.volume = 1 // 音量（0-1）
    
    // 开始播放
    window.speechSynthesis.speak(utterance.value)
  } catch (error) {
    console.error('浏览器语音合成失败:', error)
  }
}

// 组件挂载时初始化
onMounted(() => {
  // 初始化API基础URL
  interviewStore.initApiBaseUrl()
  
  // 初始化会话
  interviewStore.initSession()
  
  // 设置当前时间为访谈开始时间
  const now = new Date()
  interviewTime.value = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
});

// 来自InterviewWaiting组件的方法
// 开始麦克风检测，与HTML版本保持一致
const startMicCheck = async () => {
  isLoading.value = true
  loadingText.value = '连接访谈服务器...'
  
  try {
    if (!interviewStore.projectId) throw new Error("链接无效：缺少 Project ID")

    // 确保项目信息和AI配置已获取
    if (!interviewStore.projectInfo || !interviewStore.aiConfig) {
      console.log("项目信息或AI配置未获取，正在尝试获取...")
      await interviewStore.fetchProjectAndAIConfig()
    }

    // 步骤 2: 播放UI动画 (保持流畅的体验)
    loadingText.value = '检测环境噪音...'
    await new Promise(r => setTimeout(r, 1000))
    
    // 步骤 3: 显示检测通过信息
    loadingText.value = '检测通过，正在进入...'
    await new Promise(r => setTimeout(r, 800))

    // 步骤 4: 跳转
    interviewStore.goToInterviewPage()

  } catch (error) {
    console.error(error)
    alert(`无法开始访谈: ${error.message}\n请确认后端服务已启动 (uvicorn) 且 Project ID 正确。`)
  } finally {
    isLoading.value = false
  }
}

// 来自InterviewRunning组件的方法
// 切换到语音模式
const switchToVoiceMode = () => {
  isVoiceMode.value = true
};

// 切换到文字模式
const switchToTextMode = () => {
  isVoiceMode.value = false
  // 自动聚焦到文本输入框
  nextTick(() => {
    const textInputEl = document.getElementById('text-input');
    if (textInputEl) {
      textInputEl.focus();
    }
  });
};

// AI语音回复开关
const toggleVoiceChatMode = () => {
  isAIVoiceEnabled.value = !isAIVoiceEnabled.value;
  
  // 如果关闭语音，停止当前正在播放的语音
  if (!isAIVoiceEnabled.value) {
    window.speechSynthesis.cancel();
  }
};

// 录音功能实现，与HTML版本保持一致
const startRecording = async () => {
  try {
    isRecording.value = true;
    
    // 获取麦克风权限
    const stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
    audioStream.value = stream;
    
    // 创建媒体录制器
    mediaRecorder.value = new MediaRecorder(stream);
    audioChunks.value = [];
    
    // 数据可用事件
    mediaRecorder.value.addEventListener('dataavailable', (event) => {
      if (event.data.size > 0) {
        audioChunks.value.push(event.data);
      }
    });
    
    // 录制结束事件
    mediaRecorder.value.addEventListener('stop', async () => {
      console.log('录音结束');
      
      // 关闭媒体流
      stream.getTracks().forEach(track => track.stop());
      
      // 上传录音数据
      await uploadAudio();
    });
    
    // 开始录制
    mediaRecorder.value.start();
    console.log('开始录音');
    
  } catch (error) {
    console.error('录音失败:', error);
    alert('无法访问麦克风，请检查浏览器权限设置');
    isRecording.value = false;
  }
};

// 停止录音
const stopRecording = () => {
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    mediaRecorder.value.stop();
  }
  
  isRecording.value = false;
};

// 上传录音数据到服务器，与HTML版本保持一致
const uploadAudio = async () => {
  try {
    // 创建音频Blob
    const audioBlob = new Blob(audioChunks.value, { type: 'audio/wav' });
    
    // 创建FormData对象
    const formData = new FormData();
    formData.append('audio_file', audioBlob, 'recording.wav');
    
    // 调用API上传音频
    await interviewStore.uploadAudio(formData);
  } catch (error) {
    console.error('处理录音失败:', error);
    interviewStore.addMessage({ type: 'ai', content: '抱歉，我无法识别您的语音，请您用文字输入或者重试。' });
  }
};

// 发送文字消息
const sendMessage = (event) => {
  // 阻止浏览器的默认换行行为
  if (event) event.preventDefault();
  
  const text = textInput.value.trim();
  if(!text) return;
  
  // 显示用户消息
  interviewStore.sendMessage(text, false);
  textInput.value = '';
};

// 打断AI当前发言
const interruptAI = () => {
  // 停止当前的语音合成
  window.speechSynthesis.cancel();
  interviewStore.addMessage({ type: 'system', content: '已打断AI发言' });
  interviewStore.interruptAI();
};

// 来自InterviewEnd组件的方法
// 开始上传模拟，与HTML版本保持一致
const startUploadSimulation = () => {
  uploadComplete.value = false;
  uploadTitle.value = '正在保存记录...';
  uploadDescription.value = '请勿关闭页面，数据加密上传中';
  uploadIconClass.value = 'fas fa-cloud-upload-alt';
  
  // 动画进度
  setTimeout(() => updateProgress(180), 100);
  setTimeout(() => updateProgress(100), 800);
  setTimeout(() => {
    updateProgress(0);
    uploadTitle.value = "保存成功！";
    uploadDescription.value = "即将跳转...";
    uploadIconClass.value = "fas fa-check text-success";
  }, 1500);

  // 切换到成功视图
  setTimeout(() => {
    uploadComplete.value = true;
  }, 2500);
};

// 更新上传进度
const updateProgress = (offset) => {
  const circle = document.getElementById('upload-circle');
  if (circle) {
    circle.style.strokeDashoffset = offset;
  }
};

// 关闭页面
const closeWindow = () => {
  if(confirm("确定要离开页面吗？")) {
    window.close();
    // 某些浏览器不允许脚本关闭非脚本打开的窗口，提示用户手动关闭
    document.body.innerHTML = "<div class='flex h-screen items-center justify-center text-gray-500'>您现在可以安全关闭此浏览器窗口。</div>";
  }
};

// 来自InterviewModal组件的方法
// 打开终止确认模态框
const openTerminateModal = () => {
  interviewStore.openTerminateModal();
};

// 打开分享链接模态框
const openShareModal = () => {
  interviewStore.openShareModal();
};

// 关闭模态框
const closeModal = () => {
  interviewStore.closeModal();
};

// 确认模态框操作
const confirmModalAction = () => {
  interviewStore.confirmModalAction();
};

// 复制分享链接
const copyShareLink = async () => {
  try {
    // 复制链接到剪贴板
    await navigator.clipboard.writeText(shareLink.value);
    interviewStore.closeModal();
    // 可以添加一个提示
  } catch (error) {
    console.error('复制链接失败:', error);
  }
};
</script>

<style>
/* 全局样式 */
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  -webkit-tap-highlight-color: transparent;
}

/* 聊天气泡 */
.chat-bubble {
  max-width: 85%;
  padding: 12px 16px;
  border-radius: 18px;
  position: relative;
  line-height: 1.5;
  font-size: 15px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.chat-bubble.ai {
  background-color: #ffffff;
  color: #1f2937;
  border-top-left-radius: 4px;
}

.chat-bubble.user {
  background-color: #2563eb;
  color: white;
  border-top-right-radius: 4px;
}



/* 进度条动画 */
.progress-bar {
  transition: width 0.5s ease-out;
}

/* 隐藏滚动条 */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* 动画定义 */


@keyframes fadeIn {
  0% { opacity: 0; }
  100% { opacity: 1; }
}

@keyframes slideUp {
  0% { transform: translateY(20px); opacity: 0; }
  100% { transform: translateY(0); opacity: 1; }
}

/* 应用动画类 */
.animate-fade-in {
  animation: fadeIn 0.5s ease-out forwards;
}

.animate-slide-up {
  animation: slideUp 0.3s ease-out forwards;
}

.animate-pulse-slow {
  animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* 来自InterviewEnd组件的样式 */
.hidden {
  display: none;
}

/* 来自InterviewModal组件的样式 */
.fixed.inset-0 {
  z-index: 50;
}

.transform.scale-95 {
  animation: scaleIn 0.2s ease-out forwards;
}

@keyframes scaleIn {
  to {
    transform: scale(1);
  }
}
</style>