<template>
    <!-- 返回按钮 -->
    <div class="mb-6">
        <button @click="router.back()" class="flex items-center gap-2 text-primary hover:text-blue-700 font-medium">
            <i class="fas fa-arrow-left"></i>
            返回
        </button>
    </div>
    
    <!-- 左侧：主要配置 (占2列) -->
    <div class="lg:col-span-2 space-y-8">
        
        <!-- 1. AI身份设定 -->
        <section class="bg-white rounded-xl shadow-card p-6 border border-border-light">
            <h2 class="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
                <span class="w-8 h-8 rounded-full bg-blue-100 text-primary flex items-center justify-center text-sm font-bold">1</span>
                身份设定
            </h2>
            
            <div class="space-y-6">
                <!-- 名称 -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">AI 访谈者姓名</label>
                    <input v-model="aiConfig.name" type="text" id="ai-name" class="w-full px-4 py-2.5 border border-border-light rounded-lg input-focus" placeholder="例如：李教授">
                </div>

                <!-- 虚拟形象 -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-3">选择形象</label>
                    <div class="flex gap-4">
                        <div
                            v-for="avatar in avatarOptions"
                            :key="avatar.id"
                            :class="['avatar-option w-16 h-16 rounded-full flex items-center justify-center cursor-pointer', configState.avatar === avatar.id ? 'selected' : '']"
                            :style="{ backgroundColor: avatar.bgColor }"
                            @click="selectAvatar(avatar.id)"
                        >
                            <i :class="['fas', avatar.icon, 'text-2xl']" :style="{ color: avatar.textColor }"></i>
                        </div>
                    </div>
                </div>

                <!-- 专业背景 -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">专业背景</label>
                    <input v-model="aiConfig.role_settings.profession" type="text" id="ai-profession" class="w-full px-4 py-2.5 border border-border-light rounded-lg input-focus" placeholder="例如：拥有10年经验的用户研究专家">
                </div>
            </div>
        </section>

        <!-- 2. 访谈策略 -->
        <section class="bg-white rounded-xl shadow-card p-6 border border-border-light">
            <h2 class="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
                <span class="w-8 h-8 rounded-full bg-blue-100 text-primary flex items-center justify-center text-sm font-bold">2</span>
                访谈策略
            </h2>

            <div class="space-y-6">
                <!-- 语言风格 -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-3">语言风格</label>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-3" id="style-options">
                        <div
                            v-for="tone in toneOptions"
                            :key="tone.id"
                            :class="['radio-option p-3 rounded-lg cursor-pointer', configState.tone === tone.id ? 'selected' : '']"
                            @click="selectTone(tone.id)"
                        >
                            <div class="flex flex-col items-center gap-1">
                                <i :class="['fas', tone.icon, 'text-lg mb-1 opacity-70']"></i>
                                <span class="text-sm font-medium">{{ tone.label }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 追问深度 -->
                <div>
                    <div class="flex justify-between mb-2">
                        <label class="text-sm font-medium text-gray-700">追问深度</label>
                        <span id="depth-display" class="text-sm font-bold text-primary">{{ depthLabels[aiConfig.strategy.depth_level - 1] }} ({{ aiConfig.strategy.depth_level }})</span>
                    </div>
                    <input
                        v-model.number="aiConfig.strategy.depth_level"
                        type="range"
                        id="depth-slider"
                        min="1"
                        max="5"
                        value="3"
                        class="w-full"
                        @input="updateDepthDisplay"
                    >
                    <div class="flex justify-between text-xs text-gray-400 mt-1">
                        <span>浅尝辄止</span>
                        <span>刨根问底</span>
                    </div>
                </div>
                
                <!-- 高级提示词 -->
                <div class="pt-4 border-t border-gray-100">
                    <label class="block text-sm font-medium text-gray-700 mb-2">高级提示词 (System Prompt)</label>
                    <textarea
                        v-model="aiConfig.role_settings.custom_prompt"
                        id="custom-prompt"
                        rows="3"
                        class="w-full px-4 py-3 border border-border-light rounded-lg input-focus text-sm"
                        placeholder="可选：覆盖默认的 AI 行为指令..."
                    ></textarea>
                </div>
            </div>
        </section>
    </div>

    <!-- 右侧：话术预览 & 发布 (占1列) -->
    <div class="lg:col-span-1 space-y-6">
        
        <!-- 话术模板 -->
        <section class="bg-white rounded-xl shadow-card p-6 border border-border-light sticky top-24">
            <h3 class="font-bold text-gray-900 mb-4">话术预览</h3>
            
            <div class="space-y-4">
                <!-- 开场白 -->
                <div>
                    <label class="text-xs font-bold text-gray-400 uppercase">开场白</label>
                    <div class="mt-1 p-3 bg-blue-50 rounded-lg border border-blue-100 text-sm text-gray-700 relative group">
                        <textarea
                            v-model="aiConfig.role_settings.opening_text"
                            id="opening-text"
                            rows="3"
                            class="w-full bg-transparent border-none outline-none resize-none p-0 text-sm"
                        ></textarea>
                        <div class="absolute right-2 bottom-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <i class="fas fa-pen text-blue-300 text-xs"></i>
                        </div>
                    </div>
                </div>

                <!-- 结束语 -->
                <div>
                    <label class="text-xs font-bold text-gray-400 uppercase">结束语</label>
                    <div class="mt-1 p-3 bg-green-50 rounded-lg border border-green-100 text-sm text-gray-700 relative group">
                        <textarea
                            v-model="aiConfig.role_settings.closing_text"
                            id="closing-text"
                            rows="3"
                            class="w-full bg-transparent border-none outline-none resize-none p-0 text-sm"
                        ></textarea>
                        <div class="absolute right-2 bottom-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <i class="fas fa-pen text-green-300 text-xs"></i>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 底部大按钮 -->
            <div class="mt-8 pt-6 border-t border-gray-100">
                <button @click="saveAIConfig" id="save-btn" class="w-full bg-gray-800 hover:bg-gray-900 text-white rounded-xl py-4 font-bold text-lg shadow-lg hover:shadow-xl transition-all active:scale-95 flex items-center justify-center gap-2 mb-3">
                    <i class="fas fa-save"></i>
                    <span>保存AI配置</span>
                </button>
                <button @click="publishProject" id="publish-btn" class="w-full bg-primary hover:bg-blue-700 text-white rounded-xl py-4 font-bold text-lg shadow-lg hover:shadow-xl transition-all active:scale-95 flex items-center justify-center gap-2">
                    <i class="fas fa-rocket"></i>
                    <span>发布访谈项目</span>
                </button>
                <p class="text-xs text-center text-gray-400 mt-3">点击发布将生成访谈链接</p>
            </div>
        </section>
    </div>

    <!-- 发布成功弹窗 -->
    <div id="success-modal" class="fixed inset-0 z-50 hidden flex items-center justify-center bg-black/50 backdrop-blur-sm">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8 modal-enter relative">
            <div class="text-center">
                <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <i class="fas fa-check text-success text-4xl"></i>
                </div>
                <h3 class="text-2xl font-bold text-gray-900 mb-2">发布成功！</h3>
                <p class="text-secondary mb-6">访谈项目已生成，复制下方链接分享给受访者。</p>
            </div>
            
            <div class="bg-gray-50 rounded-xl p-4 border border-gray-200 mb-6">
                <label class="text-xs font-bold text-gray-400 uppercase mb-1 block">访谈链接 (Guest Link)</label>
                <div class="flex items-center gap-2">
                    <input type="text" id="result-link" readonly class="flex-1 bg-white border border-gray-200 rounded px-2 py-1 text-sm text-gray-600 select-all outline-none" v-model="resultLink">
                    <button @click="copyLink" class="text-primary hover:text-blue-700 font-medium text-sm px-2">复制</button>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
                <button @click="closeModal" class="py-3 px-4 border border-gray-300 rounded-xl text-gray-600 font-medium hover:bg-gray-50">稍后查看</button>
                <router-link to="/interview-list" class="py-3 px-4 bg-primary text-white rounded-xl font-medium hover:bg-blue-700 text-center block">前往监控看板</router-link>
            </div>
        </div>
    </div>

    <!-- 通用 Toast -->
    <div id="toast" class="fixed top-24 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white px-6 py-3 rounded-lg shadow-xl z-50 transition-opacity duration-300 opacity-0 pointer-events-none">
        <span id="toast-msg">{{ toastMessage }}</span>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiService from '../services/api';

const route = useRoute();
const router = useRouter();

// URL参数
const outlineId = route.query.outlineId;
const projectId = route.query.projectId;

// 状态管理
const configState = ref({
    avatar: 'blue',
    tone: 'formal'
});

// API配置
const apiUrl = ref('');

// 发布结果
const resultLink = ref('');

// Toast消息
const toastMessage = ref('');
const toastTimeout = ref(null);

// 深度级别标签
const depthLabels = ['非常浅', '较浅', '适中', '较深', '极深'];

// 语言风格选项
const toneOptions = [
    { id: 'formal', label: '专业严谨', icon: 'fa-briefcase' },
    { id: 'friendly', label: '亲和友善', icon: 'fa-heart' },
    { id: 'casual', label: '轻松活泼', icon: 'fa-coffee' },
    { id: 'rigorous', label: '理性客观', icon: 'fa-scale-balanced' }
];

// 头像选项 - 顺序对应：manager、professor、assistant、student
const avatarOptions = [
    { id: 'blue', icon: 'fa-user-tie', bgColor: '#e0f2fe', textColor: '#2563eb' }, // manager
    { id: 'green', icon: 'fa-user-graduate', bgColor: '#dcfce7', textColor: '#10b981' }, // professor
    { id: 'purple', icon: 'fa-robot', bgColor: '#f3e8ff', textColor: '#8b5cf6' }, // assistant
    { id: 'orange', icon: 'fa-smile', bgColor: '#fffbeb', textColor: '#f59e0b' } // student
];

// AI配置数据
const aiConfig = ref({
    name: '小智',
    role_settings: {
        avatar_id: 'blue',
        profession: '',
        tone: 'formal',
        custom_prompt: '',
        opening_text: '您好，我是AI访谈者小智。感谢您参与本次调研，我们的对话将严格保密，请您放心。',
        closing_text: '非常有价值的分享！感谢您的时间，本次访谈到此结束，祝您生活愉快。'
    },
    strategy: {
        depth_level: 3,
        max_duration: 1800
    }
});

// 显示Toast消息
function showToast(message) {
    toastMessage.value = message;
    const toast = document.getElementById('toast');
    toast.classList.remove('opacity-0');
    toast.classList.add('opacity-100');
    
    if (toastTimeout.value) {
        clearTimeout(toastTimeout.value);
    }
    
    toastTimeout.value = setTimeout(() => {
        toast.classList.remove('opacity-100');
        toast.classList.add('opacity-0');
    }, 3000);
}

// 更新深度显示
function updateDepthDisplay() {
    // 深度值已通过v-model绑定，自动更新
}

// API配置相关功能已移除，由全局配置处理

// 选择头像
function selectAvatar(avatarId) {
    configState.value.avatar = avatarId;
    aiConfig.value.role_settings.avatar_id = avatarId;
}

// 选择语言风格
function selectTone(toneId) {
    configState.value.tone = toneId;
    aiConfig.value.role_settings.tone = toneId;
}

// 复制链接
function copyLink() {
    const linkInput = document.getElementById('result-link');
    linkInput.select();
    navigator.clipboard.writeText(linkInput.value);
    showToast('链接已复制到剪贴板');
}

// 关闭弹窗
function closeModal() {
    const modal = document.getElementById('success-modal');
    modal.classList.add('hidden');
}

// 获取已有AI配置
async function fetchAIConfig() {
    if (!outlineId) return;
    
    try {
        const configsResult = await apiService.get(`/ai-configs/?outline_id=${outlineId}`);
        const configs = configsResult.items || [];
        
        if (configs.length > 0) {
            const config = configs[0];
            aiConfig.value = {
                name: config.name || '小智',
                role_settings: config.role_settings || {
                    avatar_id: 'blue',
                    profession: '',
                    tone: 'formal',
                    custom_prompt: '',
                    opening_text: '您好，我是AI访谈者小智。感谢您参与本次调研，我们的对话将严格保密，请您放心。',
                    closing_text: '非常有价值的分享！感谢您的时间，本次访谈到此结束，祝您生活愉快。'
                },
                strategy: config.strategy || {
                    depth_level: 3,
                    max_duration: 1800
                }
            };
            
            configState.value.avatar = aiConfig.value.role_settings.avatar_id;
            configState.value.tone = aiConfig.value.role_settings.tone;
        }
    } catch (error) {
        console.error('获取AI配置失败:', error);
        showToast(`获取AI配置失败: ${error.message}`);
    }
}

// 保存AI配置
async function saveAIConfig() {
    if (!outlineId) {
        showToast('错误：URL 中缺少 outlineId，无法保存AI配置。请从提纲页进入。');
        return null;
    }

    // 验证必填字段
    const aiName = aiConfig.value.name;
    if (!aiName.trim()) {
        showToast('错误：AI访谈者姓名不能为空！');
        return null;
    }

    const btn = document.getElementById('save-btn');
    const originalContent = btn.innerHTML;
    btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> 保存中...`;
    btn.disabled = true;

    try {
        // 准备AI配置数据
        const configPayload = {
            name: aiName,
            role_settings: aiConfig.value.role_settings,
            strategy: aiConfig.value.strategy,
            outline_id: parseInt(outlineId)
        };

        // 获取已有AI配置
        const configsResult = await apiService.get(`/ai-configs/?outline_id=${outlineId}`);
        const configs = configsResult.items || [];
        let aiConfigId = null;
        
        if (configs.length > 0) {
            aiConfigId = configs[0].id;
        }

        let configData;
        if (aiConfigId) {
            // 更新已有AI配置
            const updateResult = await apiService.put(`/ai-configs/${aiConfigId}`, configPayload);
            configData = updateResult.data || updateResult;
        } else {
            // 创建新AI配置
            const createResult = await apiService.post(`/ai-configs/`, configPayload);
            configData = createResult.data || createResult;
            
            aiConfigId = configData.id;
            
            // 如果有projectId，更新项目的AI配置ID
            if (projectId) {
                try {
                    await apiService.put(`/projects/${projectId}`, {
                        ai_config_id: aiConfigId,
                        status: 'active'
                    });
                } catch (error) {
                    console.warn('项目更新失败，但AI配置已保存:', error);
                }
            }
        }
        
        showToast('AI配置保存成功！');
        return aiConfigId;

    } catch (error) {
        console.error(error);
        showToast(`保存失败: ${error.message}`);
        return null;
    } finally {
        btn.innerHTML = originalContent;
        btn.disabled = false;
    }
}

// 发布项目
async function publishProject() {
    if (!outlineId) {
        showToast('错误：URL 中缺少 outlineId，无法发布项目。请从提纲页进入。');
        return;
    }

    const btn = document.getElementById('publish-btn');
    const originalContent = btn.innerHTML;
    btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> 处理中...`;
    btn.disabled = true;

    try {
        // 先保存AI配置
        const aiConfigId = await saveAIConfig();
        if (!aiConfigId) {
            throw new Error('AI配置保存失败，无法发布项目。请检查AI访谈者姓名是否填写。');
        }

        // 获取项目信息
        let project = null;
        
        if (projectId) {
            try {
                const projectResult = await apiService.get(`/projects/${projectId}`);
                project = projectResult.data || projectResult;
            } catch (error) {
                console.log('获取项目详情失败，尝试创建新项目:', error.message);
            }
        } else {
            const projectsResult = await apiService.get(`/projects/?outline_id=${outlineId}`);
            const projects = projectsResult.items || [];
            
            if (projects.length > 0) {
                project = projects[0];
            }
        }

        // 发布或更新项目
        const projectPayload = {
            outline_id: parseInt(outlineId),
            ai_config_id: aiConfigId,
            status: 'active'
        };

        let projectData;
        if (project) {
            // 更新已有项目
            const updateResult = await apiService.put(`/projects/${project.id}`, projectPayload);
            projectData = updateResult.data || updateResult;
        } else {
            // 创建新项目
            const createResult = await apiService.post(`/projects/`, projectPayload);
            projectData = createResult.data || createResult;
        }
        
        // 显示成功弹窗
        const guestLink = `${window.location.origin}/guest-interview?projectId=${projectData.id}`;
        resultLink.value = guestLink;
        
        const modal = document.getElementById('success-modal');
        modal.classList.remove('hidden');

    } catch (error) {
        console.error(error);
        showToast(`发布失败: ${error.message}`);
    } finally {
        btn.innerHTML = originalContent;
        btn.disabled = false;
    }
}

// 初始化
onMounted(async () => {
    // 加载API地址
    apiUrl.value = localStorage.getItem('apiBaseUrl') || '';
    
    // 获取AI配置
    await fetchAIConfig();
});
</script>

<style scoped>
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.radio-option {
    transition: all 0.2s ease;
    border: 1px solid #e2e8f0;
}

.radio-option:hover {
    border-color: #2563eb;
    background-color: #f8fafc;
}

.radio-option.selected {
    background-color: #eff6ff;
    border-color: #2563eb;
    color: #2563eb;
}

.avatar-option {
    transition: all 0.2s ease;
    border: 2px solid transparent;
}

.avatar-option.selected {
    border-color: #2563eb;
    transform: scale(1.05);
}

.input-focus:focus {
    outline: none;
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

/* 范围滑块样式优化 */
input[type=range] {
    -webkit-appearance: none;
    background: transparent;
}

input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none;
    height: 20px;
    width: 20px;
    border-radius: 50%;
    background: #2563eb;
    cursor: pointer;
    margin-top: -8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

input[type=range]::-webkit-slider-runnable-track {
    width: 100%;
    height: 4px;
    cursor: pointer;
    background: #e2e8f0;
    border-radius: 2px;
}

.container-responsive {
    max-width: 1024px;
    margin: 0 auto;
}

.modal-enter {
    animation: modalIn 0.3s ease-out forwards;
}

@keyframes modalIn {
    from {
        opacity: 0;
        transform: scale(0.95);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}
</style>