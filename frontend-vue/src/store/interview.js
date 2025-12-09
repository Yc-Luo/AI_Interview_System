import { defineStore } from 'pinia'
import apiService from '../services/api'
import AuthService from '../services/auth'
import { getParticipantId } from '../utils/identity'

export const useInterviewStore = defineStore('interview', {
  state: () => ({
    // 页面状态
    currentPage: 'waiting', // waiting, interview, end
    
    // 模态框状态
    modalVisible: false,
    modalType: 'terminate', // terminate, share
    
    // 项目和AI配置
    projectId: '',
    sessionId: '',
    visitorUuid: '',
    projectInfo: null,
    aiConfig: null,
    
    // 访谈消息
    messages: [],
    
    // 加载状态
    isLoading: false,
    loadingText: '连接访谈服务器...',
    
    // 错误信息
    error: null
  }),
  
  getters: {
    // 获取当前页面是否为访谈进行页
    isInterviewPage: (state) => state.currentPage === 'interview',
    
    // 获取当前页面是否为结束页
    isEndPage: (state) => state.currentPage === 'end',
    
    // 获取是否正在加载
    isLoading: (state) => state.isLoading,
    
    // 获取是否有错误
    hasError: (state) => state.error !== null
  },
  
  actions: {
    // 初始化API基础URL，与HTML版本保持一致
    initApiBaseUrl() {
      // 在前端开发环境中，我们不设置具体的baseURL，让请求走Vue的代理配置
      // 这样可以避免CORS问题
      const apiBaseUrl = '';
      
      // 设置 API 基础 URL
      AuthService.setApiBaseUrl(apiBaseUrl);
      // 更新api实例的baseURL
      apiService.setBaseURL(apiBaseUrl);
      
      console.log('API Base URL set to:', apiBaseUrl);
    },
    
    // 获取URL参数
    getUrlParam(name) {
      const urlParams = new URLSearchParams(window.location.search)
      return urlParams.get(name)
    },
    
    // 初始化会话
    async initSession() {
      this.setLoading(true, '连接访谈服务器...')
      this.clearError()
      
      try {
        // 获取URL参数
        this.projectId = this.getUrlParam('projectId')
        this.sessionId = this.getUrlParam('sessionId') || localStorage.getItem('interviewSessionId')
        
        // 生成或获取访客唯一UUID（基于项目ID）
        this.visitorUuid = getParticipantId(this.projectId)
        
        console.log("开始初始化会话")
        console.log("projectId:", this.projectId)
        console.log("currentSessionId:", this.sessionId)
        
        if (!this.projectId) {
          throw new Error("链接无效：缺少 Project ID")
        }

        // 先获取项目信息和AI配置信息
        await this.fetchProjectAndAIConfig()
        
        // 如果没有会话ID，请求后端生成新的会话ID
        if (!this.sessionId) {
          console.log("正在请求创建新会话...")
          // apiService.post 已经直接返回 data.data || data，所以不需要再访问 .data 字段
          const resData = await apiService.post('/sessions', {
            project_id: this.projectId,
            visitor_uuid: this.visitorUuid,
            interviewee_info: {
              userAgent: navigator.userAgent,
              screen: `${window.screen.width}x${window.screen.height}`,
              visitor_uuid: this.visitorUuid
            }
          })
          this.sessionId = resData.session_id
          console.log("新会话创建成功:", this.sessionId)
          
          // 将会话ID存储在 localStorage 中
          localStorage.setItem('interviewSessionId', this.sessionId)
          
          // 更新URL，添加会话ID参数
          const url = new URL(window.location.href)
          url.searchParams.set('sessionId', this.sessionId)
          window.history.replaceState({}, '', url)
        }
        
        return true
      } catch (error) {
        console.error("初始化会话失败:", error)
        console.error("错误详情:", error.stack)
        this.setError(`初始化会话失败: ${error.message}`)
        return false
      } finally {
        this.setLoading(false)
      }
    },
    
    // 获取项目信息和AI配置信息
    async fetchProjectAndAIConfig() {
      this.setLoading(true, '获取访谈信息...')
      this.clearError()
      
      try {
        // 获取项目信息
        console.log("开始请求项目信息...")
        // apiService.get 已经直接返回 data.data || data，所以不需要再访问 .data 字段
        this.projectInfo = await apiService.get(`/projects/${this.projectId}`)
        console.log("项目信息获取成功:", this.projectInfo)

        // 获取AI配置信息
        console.log("开始请求AI配置信息...")
        console.log("ai_config_id:", this.projectInfo.ai_config_id)
        // apiService.get 已经直接返回 data.data || data，所以不需要再访问 .data 字段
        this.aiConfig = await apiService.get(`/ai-configs/${this.projectInfo.ai_config_id}`)
        console.log("AI配置信息获取成功:", this.aiConfig)

        console.log("访谈信息更新完成")
        return true
      } catch (error) {
        console.error("获取项目信息失败:", error)
        console.error("错误详情:", error.stack)
        this.setError(`获取访谈信息失败: ${error.message}`)
        // 重新抛出错误，让调用者知道发生了错误
        throw error
      } finally {
        this.setLoading(false)
      }
    },
    
    // 开始麦克风检测
    async startMicCheck() {
      this.setLoading(true, '检测麦克风...')
      this.clearError()
      
      try {
        if (!this.projectId) throw new Error("链接无效：缺少 Project ID")

        // 确保项目信息和AI配置已获取
        if (!this.projectInfo || !this.aiConfig) {
          console.log("项目信息或AI配置未获取，正在尝试获取...")
          await this.fetchProjectAndAIConfig()
        }

        // 跳转到访谈进行页
        this.goToInterviewPage()

        return true
      } catch (error) {
        console.error(error)
        this.setError(`无法开始访谈: ${error.message}\n请确认后端服务已启动 (uvicorn) 且 Project ID 正确。`)
        return false
      } finally {
        this.setLoading(false)
      }
    },
    
    // 跳转到访谈进行页
    goToInterviewPage() {
      this.currentPage = 'interview'
      
      // 清空消息列表
      this.messages = []
      
      // 模拟进入后的首条消息延迟
      setTimeout(() => {
        this.addMessage({ type: "system", content: "已连接到 AI 访谈助手" })
        // 触发 AI 的开场白
        const openingText = this.aiConfig?.role_settings?.opening_text || "同学你好，我是AI访谈助手。很高兴今天能和你聊聊。"
        this.addMessage({ type: "ai", content: openingText })
      }, 800)
    },
    
    // 发送消息
    async sendMessage(content, isVoice = false) {
      this.clearError()
      
      // 添加用户消息
      this.addMessage({ type: "user", content, isVoice })
      
      try {
        // 调用AI API获取回复
        return await this.callAIAPI(content)
      } catch (error) {
        console.error('发送消息失败:', error)
        this.setError(`发送消息失败: ${error.message}`)
        return false
      }
    },
    
    // 上传音频并调用AI API，与HTML版本保持一致
    async uploadAudio(formData) {
      this.clearError()
      
      try {
        // 调用语音转文字API
        // 注意：使用fetch而不是api.request，因为api.request默认会将body转换为JSON
        // 而FormData需要特殊处理
        const response = await fetch(`${apiService.baseURL}/api/speech-to-text`, {
          method: 'POST',
          body: formData,
          // 不需要Content-Type，浏览器会自动设置为multipart/form-data
          credentials: 'include',
          mode: 'cors'
        })
        
        if (!response.ok) {
          throw new Error(`API请求失败: ${response.status} ${response.statusText}`)
        }
        
        const result = await response.json()
        
        // 处理统一的API响应格式
        // 注意：fetch返回的是原始响应，需要自己处理json()，所以仍需访问result.data
        const transcribedText = result.data.text
        
        // 显示转录结果
        this.addMessage({ type: "user", content: transcribedText, isVoice: true })
        
        // 调用AI API获取回复
        return await this.callAIAPI(transcribedText)
      } catch (error) {
        console.error('处理录音失败:', error)
        this.addMessage({ type: "ai", content: "抱歉，我无法识别您的语音，请您用文字输入或者重试。" })
        this.setError(`处理录音失败: ${error.message}`)
        return false
      }
    },
    
    // 调用AI API获取回复
    async callAIAPI(content) {
      this.setLoading(true, 'AI正在思考...')
      this.clearError()
      
      try {
        // 调用真实的AI API，使用正确的路径格式
        const response = await apiService.post('/chat', {
          session_id: this.sessionId,
          content: content
        })
        
        // 处理统一的API响应格式
        // 注意：apiService.post已经返回了处理过的数据（data.data || data），所以直接使用response
        const responseData = response || {}
        const replyContent = responseData.reply || '抱歉，我暂时无法回答您的问题。'
        
        // 显示AI回复
        this.addMessage({ type: "ai", content: replyContent })
        
        // 检查是否需要结束访谈
        if (replyContent.includes('[END]')) {
          // 访谈结束，显示结束页面
          setTimeout(() => {
            this.goToEndPage()
          }, 2000)
        }
        
        return true
      } catch (error) {
        // 显示错误信息
        console.error('AI API调用失败:', error)
        this.addMessage({ type: "ai", content: "抱歉，我刚才走神了，能请您再说一遍吗？" })
        this.setError(`AI API调用失败: ${error.message}`)
        return false
      } finally {
        this.setLoading(false)
      }
    },
    
    // 添加消息
    addMessage(message) {
      this.messages.push(message)
    },
    
    // 打断AI当前发言
    interruptAI() {
      // 停止当前的语音合成
      window.speechSynthesis.cancel()
      this.addMessage({ type: "system", content: "已打断AI发言" })
    },
    
    // 跳转到结束页面
    async goToEndPage() {
      this.currentPage = 'end'
      
      // 如果有会话ID，调用API结束会话，记录结束时间
      if (this.sessionId) {
        try {
          await apiService.put(`/sessions/${this.sessionId}/end`)
          console.log('会话结束时间已更新')
        } catch (error) {
          console.error('更新会话结束时间失败:', error)
          // 即使失败也不影响用户体验，只是没有记录结束时间
        }
      }
    },
    
    // 打开终止确认模态框
    openTerminateModal() {
      this.modalType = 'terminate'
      this.modalVisible = true
    },
    
    // 打开分享链接模态框
    openShareModal() {
      this.modalType = 'share'
      this.modalVisible = true
    },
    
    // 关闭模态框
    closeModal() {
      this.modalVisible = false
    },
    
    // 确认模态框操作
    confirmModalAction() {
      if (this.modalType === 'terminate') {
        // 结束访谈
        this.goToEndPage()
      }
      this.modalVisible = false
    },
    
    // 设置加载状态
    setLoading(isLoading, text = '加载中...') {
      this.isLoading = isLoading
      this.loadingText = text
    },
    
    // 设置错误信息
    setError(error) {
      this.error = error
    },
    
    // 清空错误信息
    clearError() {
      this.error = null
    },
    
    // 重置状态
    resetState() {
      this.currentPage = 'waiting'
      this.modalVisible = false
      this.modalType = 'terminate'
      this.projectId = ''
      this.sessionId = ''
      this.projectInfo = null
      this.aiConfig = null
      this.messages = []
      this.isLoading = false
      this.loadingText = '连接访谈服务器...'
      this.error = null
    }
  }
})