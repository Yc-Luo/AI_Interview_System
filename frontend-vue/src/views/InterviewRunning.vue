<template>
  <div id="page-interview" class="fixed inset-0 bg-gray-50 z-20 flex flex-col">
    <!-- 聊天区域 -->
    <main id="chat-container" class="flex-1 overflow-y-auto p-4 space-y-6 no-scrollbar pb-32">
      <!-- 历史记录占位 -->
      <div id="interview-start-time" class="text-center text-xs text-gray-400 my-4">访谈开始 - {{ interviewTime }}</div>
      
      <!-- 聊天消息 -->
      <div v-for="(message, index) in messages" :key="index" :class="['flex gap-3', message.type === 'user' ? 'flex-row-reverse' : ''] + ' animate-fade-in'">
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
            @keydown.enter.exact="sendTextMessage"
            @keydown.enter.shift="$event.preventDefault(); textInput += '\n'"
          ></textarea>
        </div>
        
        <!-- 发送文字内容按钮 -->
        <button 
          @click="sendTextMessage" 
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
            class="w-full h-12 bg-gray-50 border border-gray-200 text-gray-600 rounded-full flex items-center justify-center gap-2 active:bg-blue-500 active:text-white transition-all relative overflow-hidden select-none touch-none focus:outline-none focus:ring-0 focus:border-transparent"
            :class="{ recording: isRecording }"
          >
            <div class="recording-wave"></div>
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
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router';
import apiService from '../services/api';

const route = useRoute();

// URL参数
const projectId = route.query.projectId;

// 响应式数据
const interviewTime = ref('');
const isVoiceMode = ref(false); // 默认文字模式
const isRecording = ref(false);
const textInput = ref('');
const audioStream = ref(null);
const mediaRecorder = ref(null);
const audioChunks = ref([]);
const messages = ref([]);
const isLoading = ref(false);
const aiConfig = ref(null);

// 计算属性
const aiIconClass = computed(() => {
  const avatarIconMap = {
    'blue': 'fas fa-user-tie',
    'green': 'fas fa-user-graduate',
    'purple': 'fas fa-robot',
    'orange': 'fas fa-smile'
  }
  return avatarIconMap[aiConfig?.value?.role_settings?.avatar_id] || 'fas fa-user-tie'
});

// 生命周期钩子
onMounted(() => {
  // 设置当前时间为访谈开始时间
  const now = new Date();
  interviewTime.value = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  
  // 加载AI配置
  loadAIConfig();
  
  // 添加初始系统消息
  appendSystemMsg('访谈开始');
});

// 加载AI配置
async function loadAIConfig() {
  try {
    const projectResult = await apiService.get(`/projects/${projectId}`);
    const aiConfigId = projectResult.ai_config_id;
    
    if (aiConfigId) {
      const aiConfigResult = await apiService.get(`/ai-configs/${aiConfigId}`);
      aiConfig.value = aiConfigResult;
    }
  } catch (error) {
    console.error('加载AI配置失败:', error);
    appendSystemMsg('加载AI配置失败');
  }
}

// 切换到语音模式
const switchToVoiceMode = () => {
  isVoiceMode.value = true;
};

// 切换到文字模式
const switchToTextMode = () => {
  isVoiceMode.value = false;
  // 自动聚焦到文本输入框
  nextTick(() => {
    const textInputEl = document.getElementById('text-input');
    if (textInputEl) {
      textInputEl.focus();
    }
  });
};

// 开始录音
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
      await uploadAudio();
    });
    
    // 开始录制
    mediaRecorder.value.start();
    
    appendSystemMsg('开始录音');
  } catch (error) {
    console.error('录音失败:', error);
    isRecording.value = false;
  }
};

// 停止录音
const stopRecording = () => {
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    mediaRecorder.value.stop();
  }
  
  isRecording.value = false;
  
  // 关闭媒体流
  if (audioStream.value) {
    audioStream.value.getTracks().forEach(track => track.stop());
  }
  
  appendSystemMsg('录音结束');
};

// 上传录音数据到服务器
const uploadAudio = async () => {
  try {
    // 显示上传状态
    appendSystemMsg('正在处理录音...');
    
    // 创建音频Blob
    const audioBlob = new Blob(audioChunks.value, { type: 'audio/wav' });
    
    // 创建FormData对象
    const formData = new FormData();
    formData.append('audio_file', audioBlob, 'recording.wav');
    
    // 调用API上传音频
    const response = await apiService.post(`/projects/${projectId}/interview/audio/`, formData);
    appendUserMessage(response.text, true);
    
    // 获取AI回复
    await getAIResponse(response.text);
  } catch (error) {
    console.error('处理录音失败:', error);
    appendAIMessage('抱歉，我无法识别您的语音，请您用文字输入或者重试。');
  }
};

// 发送文字消息
const sendTextMessage = () => {
  const text = textInput.value.trim();
  if(!text) return;
  
  // 显示用户消息
  appendUserMessage(text, false);
  textInput.value = '';
  
  // 获取AI回复
  getAIResponse(text);
};

// 获取AI回复
const getAIResponse = async (userText) => {
  try {
    isLoading.value = true;
    
    // 调用API获取AI回复
    const response = await apiService.post(`/projects/${projectId}/interview/text/`, {
      user_input: userText
    });
    
    // 显示AI回复
    appendAIMessage(response.response);
    
    // 自动语音合成（如果在语音模式下）
    if (isVoiceMode.value) {
      speak(response.response);
    }
  } catch (error) {
    console.error('获取AI回复失败:', error);
    appendAIMessage('抱歉，我暂时无法回复，请稍后重试。');
  } finally {
    isLoading.value = false;
  }
};

// 语音合成
const speak = (text) => {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'zh-CN';
  window.speechSynthesis.speak(utterance);
};

// 打断AI当前发言
const interruptAI = () => {
  // 停止当前的语音合成
  window.speechSynthesis.cancel();
  appendSystemMsg('已打断AI发言');
};

// 添加系统消息
const appendSystemMsg = (text) => {
  messages.value.push({ type: 'system', content: text });
  scrollToBottom();
};

// 添加用户消息
const appendUserMessage = (text, isVoice = false) => {
  messages.value.push({ type: 'user', content: text, isVoice });
  scrollToBottom();
};

// 添加AI消息
const appendAIMessage = (text) => {
  messages.value.push({ type: 'ai', content: text });
  scrollToBottom();
};

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    const chatContainer = document.getElementById('chat-container');
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  });
};
</script>

<style scoped>
/* 隐藏滚动条 */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
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

/* 录音按钮波纹 */
.recording-wave {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid #2563eb;
  opacity: 0;
  pointer-events: none;
}

.recording .recording-wave {
  animation: wave 2s infinite;
  opacity: 1;
}

/* 淡入动画 */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}
</style>