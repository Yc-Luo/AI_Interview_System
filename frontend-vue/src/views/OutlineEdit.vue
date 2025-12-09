<template>
      <!-- 顶部按钮栏 -->
      <div class="flex justify-between items-center mb-6">
        <button @click="goBack" class="flex items-center gap-1 text-gray-600 hover:text-primary transition-colors">
          <i class="fas fa-arrow-left"></i> 返回
        </button>
        <div class="flex gap-3">
          <button @click="saveOutline" class="bg-primary hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl font-bold transition-colors">
            保存
          </button>
          <button @click="handleNext" class="bg-white border-2 border-primary text-primary hover:bg-blue-50 px-6 py-2.5 rounded-xl font-bold transition-colors">
            下一步 <i class="fas fa-arrow-right ml-1"></i>
          </button>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-sm p-6 mb-6 border border-gray-200">
        <label class="block text-sm font-bold text-gray-700 mb-2">提纲标题 <span class="text-red-500">*</span></label>
        <input v-model="outline.title" type="text" id="outline-title" class="w-full px-4 py-2 border rounded-lg focus:border-blue-500 outline-none font-bold text-lg" placeholder="例如：2024年用户需求调研">
        
        <label class="block text-sm font-bold text-gray-700 mt-4 mb-2">描述</label>
        <input v-model="outline.description" type="text" id="outline-desc" class="w-full px-4 py-2 border rounded-lg focus:border-blue-500 outline-none" placeholder="简述访谈目的...">
      </div>

      <div id="modules-container" class="space-y-6">
        <div v-for="(module, mIdx) in outline.modules" :key="`module-${mIdx}`" class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div class="bg-gray-50 px-6 py-3 border-b flex justify-between items-center">
            <input v-model="module.title" type="text" class="bg-transparent font-bold text-gray-700 outline-none" placeholder="模块标题">
            <button @click="removeModule(mIdx)" class="text-gray-400 hover:text-red-500"><i class="fas fa-trash"></i></button>
          </div>
          <div class="p-6 space-y-4">
            <div v-for="(question, qIdx) in module.questions" :key="`question-${mIdx}-${qIdx}`" class="question-item pl-4 flex gap-3">
              <span class="text-xs font-bold text-gray-400 mt-3">Q{{ qIdx+1 }}</span>
              <div class="flex-1">
                <div class="flex items-start gap-2">
                  <textarea
                    v-model="question.content"
                    rows="1"
                    class="flex-1 border-b focus:border-blue-500 outline-none py-2 dynamic-textarea"
                    placeholder="输入问题..."
                    @input="autoResize($event.target)"
                  ></textarea>
                  <button @click="removeQuestion(mIdx, qIdx)" class="text-red-400 hover:text-red-600 w-6 h-6 flex items-center justify-center rounded-full bg-red-50 hover:bg-red-100 transition-colors mt-1">
                    <i class="fas fa-times text-xs"></i>
                  </button>
                </div>
                <div class="mt-2">
                  <div class="flex items-center gap-2 text-sm text-gray-500">
                    <label class="flex items-center gap-1 cursor-pointer">
                      <input
                        v-model="question.is_key_question"
                        type="checkbox"
                      > 关键问题
                    </label>
                  </div>
                  <div class="mt-2 space-y-2">
                    <div v-for="(direction, dIdx) in question.follow_up_directions" :key="`direction-${mIdx}-${qIdx}-${dIdx}`" class="flex items-center gap-2">
                      <button @click="addFollowUpDirection(mIdx, qIdx, dIdx)" class="text-primary hover:text-blue-700 w-6 h-6 flex items-center justify-center rounded-full bg-blue-50 hover:bg-blue-100 transition-colors">+</button>
                      <textarea
                        :value="direction"
                        @input="updateFollowUpDirection(mIdx, qIdx, dIdx, $event.target.value)"
                        rows="1"
                        class="bg-transparent border-b outline-none text-xs followup-textarea flex-1"
                        placeholder="+ 追问方向"
                      ></textarea>
                      <button @click="removeFollowUpDirection(mIdx, qIdx, dIdx)" class="text-grey-400 hover:text-grey-600 w-6 h-6 flex items-center justify-center rounded-full bg-grey-50 hover:bg-grey-100 transition-colors">
                        <i class="fas fa-times text-xs"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <button @click="addQuestion(mIdx)" class="w-full py-2 border border-dashed rounded text-gray-400 hover:text-blue-500 hover:border-blue-500 text-sm">+ 添加问题</button>
          </div>
        </div>
      </div>

      <div class="mt-8 text-center">
        <button @click="addModule" class="bg-white border-2 border-dashed border-gray-300 text-gray-500 px-8 py-3 rounded-xl hover:border-blue-500 hover:text-blue-600 transition-all font-bold">
          <i class="fas fa-plus-circle mr-2"></i> 添加新模块
        </button>
      </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiService from '../services/api';

const route = useRoute();
const router = useRouter();

// 状态管理
const outline = ref({
  title: '',
  description: '',
  modules: [{
    title: '基本信息',
    questions: [{
      content: '',
      is_key_question: false,
      follow_up_directions: ['']
    }]
  }]
});

const savedOutlineId = ref(null);

// 动态调整textarea高度
function autoResize(textarea) {
  textarea.style.height = 'auto';
  textarea.style.height = textarea.scrollHeight + 'px';
}

// 动态调整textarea宽度
function autoResizeWidth(textarea) {
  const temp = document.createElement('span');
  temp.style.visibility = 'hidden';
  temp.style.position = 'absolute';
  temp.style.whiteSpace = 'nowrap';
  temp.style.font = window.getComputedStyle(textarea).font;
  temp.style.padding = window.getComputedStyle(textarea).padding;
  temp.textContent = textarea.value || textarea.placeholder;
  document.body.appendChild(temp);
  
  const width = temp.offsetWidth + 40;
  document.body.removeChild(temp);
  
  const minWidth = 120;
  const maxWidth = 300;
  textarea.style.width = Math.max(minWidth, Math.min(maxWidth, width)) + 'px';
}

// 更新追问方向
function updateFollowUpDirection(mIdx, qIdx, dIdx, value) {
  outline.value.modules[mIdx].questions[qIdx].follow_up_directions[dIdx] = value;
}

// 数据操作
function addModule() {
  outline.value.modules.push({
    title: '新模块',
    questions: [{
      content: '',
      is_key_question: false,
      follow_up_directions: ['']
    }]
  });
  // 在下一个事件循环中调整textarea大小
  nextTick(() => {
    const textareas = document.querySelectorAll('.dynamic-textarea, .followup-textarea');
    textareas.forEach(textarea => {
      autoResize(textarea);
      if (textarea.classList.contains('followup-textarea')) {
        autoResizeWidth(textarea);
      }
    });
  });
}

function removeModule(mIdx) {
  if (confirm('确定删除?')) {
    outline.value.modules.splice(mIdx, 1);
  }
}

function addQuestion(mIdx) {
  outline.value.modules[mIdx].questions.push({
    content: '',
    is_key_question: false,
    follow_up_directions: ['']
  });
  // 在下一个事件循环中调整textarea大小
  nextTick(() => {
    const textareas = document.querySelectorAll('.dynamic-textarea, .followup-textarea');
    textareas.forEach(textarea => {
      autoResize(textarea);
      if (textarea.classList.contains('followup-textarea')) {
        autoResizeWidth(textarea);
      }
    });
  });
}

function removeQuestion(mIdx, qIdx) {
  outline.value.modules[mIdx].questions.splice(qIdx, 1);
}

function addFollowUpDirection(mIdx, qIdx, dIdx) {
  outline.value.modules[mIdx].questions[qIdx].follow_up_directions.splice(dIdx + 1, 0, '');
  // 在下一个事件循环中调整textarea大小
  nextTick(() => {
    const textareas = document.querySelectorAll('.dynamic-textarea, .followup-textarea');
    textareas.forEach(textarea => {
      autoResize(textarea);
      if (textarea.classList.contains('followup-textarea')) {
        autoResizeWidth(textarea);
      }
    });
  });
}

function removeFollowUpDirection(mIdx, qIdx, dIdx) {
  if (outline.value.modules[mIdx].questions[qIdx].follow_up_directions.length <= 1) {
    return;
  }
  outline.value.modules[mIdx].questions[qIdx].follow_up_directions.splice(dIdx, 1);
}

// 返回上一页
function goBack() {
  router.go(-1);
}

// 保存提纲
async function saveOutline() {
  try {
    // 验证必填项
    if (!outline.value.title.trim()) {
      alert('请输入提纲标题');
      return;
    }

    // 发送保存请求
    let response;
    if (savedOutlineId.value) {
      // 更新现有提纲
      response = await apiService.put(`/outlines/${savedOutlineId.value}`, outline.value);
    } else {
      // 创建新提纲
      response = await apiService.post('/outlines/', outline.value);
      savedOutlineId.value = response.id;
    }

    alert('提纲保存成功');
  } catch (error) {
    console.error('保存提纲失败:', error);
    alert(`保存失败: ${error.message}`);
  }
}

// 下一步
async function handleNext() {
  try {
    // 先保存提纲
    if (!outline.value.title.trim()) {
      alert('请输入提纲标题');
      return;
    }

    let outlineId = savedOutlineId.value;
    if (!outlineId) {
      // 创建新提纲
      const response = await apiService.post('/outlines/', outline.value);
      outlineId = response.id;
    } else {
      // 更新现有提纲
      await apiService.put(`/outlines/${outlineId}`, outline.value);
    }

    // 跳转到AI配置页面
    router.push(`/ai-config?outlineId=${outlineId}`);
  } catch (error) {
    console.error('保存并跳转失败:', error);
    alert(`操作失败: ${error.message}`);
  }
}

// 获取单个提纲详情
async function fetchOutlineDetail(outlineId) {
  try {
    const data = await apiService.get(`/outlines/${outlineId}`);
    return data.id ? data : null;
  } catch (e) {
    console.error('获取提纲详情失败:', e);
    alert(`获取提纲详情失败: ${e.message}`);
    return null;
  }
}

// 初始化
async function init() {
  const outlineId = route.query.outlineId;
  if (outlineId) {
    savedOutlineId.value = outlineId;
    const outlineData = await fetchOutlineDetail(outlineId);
    if (outlineData) {
      outline.value = {
        ...outlineData,
        modules: outlineData.modules.map(module => ({
          ...module,
          questions: module.questions.map(question => ({
            ...question,
            follow_up_directions: question.follow_up_directions || ['']
          }))
        }))
      };
    }
  }
  
  // 在下一个事件循环中调整textarea大小
  nextTick(() => {
    const textareas = document.querySelectorAll('.dynamic-textarea, .followup-textarea');
    textareas.forEach(textarea => {
      autoResize(textarea);
      if (textarea.classList.contains('followup-textarea')) {
        autoResizeWidth(textarea);
      }
    });
  });
}

onMounted(() => {
  init();
});
</script>

<style scoped>
.question-item {
  border-left: 3px solid transparent;
  transition: all 0.2s;
}

.question-item:focus-within {
  border-left-color: #2563eb;
  background-color: #f8fafc;
}

.dynamic-textarea {
  resize: none;
  overflow: hidden;
  transition: all 0.2s;
}

.followup-textarea {
  resize: none;
  overflow: hidden;
  transition: all 0.2s;
}
</style>