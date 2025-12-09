# 前端项目结构说明

## 项目概述

本项目是基于Vue 3的AI访谈智能体前端应用，采用组件化设计，实现了访谈提纲管理、AI配置、访谈进行等核心功能。

## 目录结构

```
src/
├── assets/           # 静态资源文件
├── components/       # 可复用组件
│   ├── config/       # 配置相关组件
│   ├── interview/    # 访谈相关组件
│   ├── layout/       # 布局组件
│   └── outline/      # 提纲编辑组件
├── router/           # 路由配置
├── services/         # 服务层
├── store/            # 状态管理
├── views/            # 页面组件
├── api.js            # API请求封装
├── App.vue           # 根组件
├── index.css         # 全局样式
└── main.js           # 入口文件
```

## 目录详细说明

### 1. assets/

静态资源文件目录，包含图片、图标等静态资源。

- `logo.png` - 项目Logo图片

### 2. components/

可复用组件目录，根据功能划分为多个子目录，便于维护和管理。

#### 2.1 components/config/

配置相关组件，用于AI配置和系统设置。

- **AIConfig.vue** - AI配置组件，设置AI访谈者身份和策略
- **Settings.vue** - 系统设置组件，管理账户和系统设置

#### 2.2 components/interview/

访谈相关组件，处理访谈过程中的各种状态和交互。

- **InterviewEnd.vue** - 访谈结束页面，显示感谢信息和分享选项
- **InterviewList.vue** - 访谈列表组件，展示和管理访谈项目
- **InterviewModal.vue** - 模态框组件，用于访谈中的各种确认和提示
- **InterviewRunning.vue** - 访谈进行组件，处理实时访谈交互
- **InterviewWaiting.vue** - 访谈等待页面，进行麦克风检查和准备

#### 2.3 components/layout/

布局组件，定义应用的整体结构和导航。

- **MainLayout.vue** - 主布局组件，包含顶部导航、侧边栏和内容区域

#### 2.4 components/outline/

提纲编辑组件，用于创建和管理访谈提纲。

- **OutlineEdit.vue** - 提纲编辑组件，支持动态添加模块、问题和追问方向

### 3. router/

路由配置目录，定义应用的路由规则和导航。

- **index.js** - 路由配置文件，包含所有页面的路由定义

### 4. services/

服务层目录，封装API请求和业务逻辑。

- **api.js** - API请求封装，处理与后端的通信
- **auth.js** - 认证服务，处理用户登录、注册和令牌管理

### 5. store/

状态管理目录，使用Pinia管理应用状态。

- **interview.js** - 访谈状态管理，管理访谈过程中的数据和状态
- **user.js** - 用户状态管理，管理用户信息和认证状态

### 6. views/

页面组件目录，对应应用的各个页面。

- **AIConfig.vue** - AI配置页面，使用config/AIConfig组件
- **GuestInterview.vue** - 嘉宾访谈页面，集成访谈相关组件
- **Home.vue** - 工作台页面，显示统计信息和快捷操作
- **InterviewList.vue** - 访谈列表页面，使用interview/InterviewList组件
- **InterviewRunning.vue** - 访谈进行页面，使用interview/InterviewRunning组件
- **Login.vue** - 登录页面
- **OutlineEdit.vue** - 提纲编辑页面，使用outline/OutlineEdit组件
- **OutlineList.vue** - 提纲列表页面
- **Register.vue** - 注册页面
- **Settings.vue** - 设置页面，使用config/Settings组件

## 核心组件关系

```
App.vue
├── MainLayout.vue (根据路由元信息动态加载)
│   └── 页面组件 (views/下的组件)
│       └── 功能组件 (components/下的组件)
└── 无布局页面 (如Login、Register等)
```

## 路由系统

路由配置采用懒加载方式，提高应用初始加载速度。路由元信息中包含：

- `requiresAuth` - 是否需要认证
- `layout` - 使用的布局类型（main或empty）

## 状态管理

使用Pinia进行状态管理，主要包含：

- **user** - 用户信息和认证状态
- **interview** - 访谈过程中的状态和数据

## 技术栈

- Vue 3 (Composition API)
- Vue Router 4
- Pinia
- Tailwind CSS
- Axios (API请求)

## 开发流程

1. **组件开发**：根据功能需求，在对应的components子目录下创建组件
2. **页面开发**：在views目录下创建页面组件，集成所需的功能组件
3. **路由配置**：在router/index.js中添加新页面的路由
4. **状态管理**：如果需要全局状态，在store目录下创建新的store
5. **样式设计**：使用Tailwind CSS进行样式设计

## 最佳实践

1. **组件化设计**：将功能拆分为可复用的组件
2. **单一职责原则**：每个组件只负责一个功能
3. **清晰的命名**：组件和文件命名清晰，便于理解
4. **代码注释**：关键代码添加注释，提高可维护性
5. **响应式设计**：确保页面在不同设备上都能正常显示

## 项目启动

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run serve

# 构建生产版本
npm run build
```

## 访问地址

开发环境：http://localhost:8080/

## 注意事项

1. 所有API请求都通过services/api.js封装，统一处理错误和认证
2. 组件之间的通信优先使用props和emit，复杂状态使用Pinia
3. 页面组件应尽量保持简洁，将复杂逻辑封装到功能组件中
4. 样式使用Tailwind CSS，尽量避免内联样式

## 后续优化方向

1. 增加单元测试和E2E测试
2. 优化组件性能，减少不必要的渲染
3. 完善错误处理和用户反馈
4. 增加国际化支持
5. 优化移动端体验

---

以上是前端项目的结构说明，希望能帮助开发者快速了解项目架构和组件关系。