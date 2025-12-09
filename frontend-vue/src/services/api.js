// 统一的API请求封装，与原api.js保持一致
import AuthService from './auth';

class API {
    constructor() {
        // 使用相对路径，让请求走代理
        this.baseURL = '';
    }
    
    // 设置基础URL
    // eslint-disable-next-line no-unused-vars
    setBaseURL(url) {
        this.baseURL = url;
    }
    
    // 获取完整URL
    getFullURL(endpoint) {
        if (endpoint.startsWith('http://') || endpoint.startsWith('https://')) {
            return endpoint;
        }
        
        // 分离路径和查询参数
        const [path, query] = endpoint.split('?', 2);
        
        // 确保路径以/开头
        let normalizedPath = path;
        if (!normalizedPath.startsWith('/')) {
            normalizedPath = `/${normalizedPath}`;
        }

        // 【关键修复】检测并移除路径末尾的斜杠 /
        // 这可以防止后端返回 307 Redirect，解决手机端 POST 请求 Body 丢失的问题
        if (normalizedPath.endsWith('/')) {
            normalizedPath = normalizedPath.slice(0, -1);
        }

        // 统一添加/api前缀，确保请求URL格式正确
        if (!normalizedPath.startsWith('/api')) {
            normalizedPath = `/api${normalizedPath}`;
        }
        
        // 重新组合路径和查询参数
        let finalEndpoint = normalizedPath;
        if (query) {
            finalEndpoint = `${finalEndpoint}?${query}`;
        }
       
        return `${this.baseURL}${finalEndpoint}`;
    }
    
    // 显示加载状态
    showLoading() {
        let loadingEl = document.getElementById('global-loading');
        if (!loadingEl) {
            loadingEl = document.createElement('div');
            loadingEl.id = 'global-loading';
            loadingEl.style.cssText = `
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                background-color: rgba(37, 99, 235, 0.9);
                color: white;
                padding: 10px 20px;
                border-radius: 25px;
                display: flex;
                align-items: center;
                gap: 8px;
                z-index: 9999;
                font-size: 14px;
                box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
            `;
            loadingEl.innerHTML = `
                <div style="width: 16px; height: 16px; border: 2px solid rgba(255, 255, 255, 0.5); border-top: 2px solid white; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                <div>加载中...</div>
                <style>
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                </style>
            `;
            document.body.appendChild(loadingEl);
        }
        loadingEl.style.display = 'flex';
    }
    
    // 隐藏加载状态
    hideLoading() {
        const loadingEl = document.getElementById('global-loading');
        if (loadingEl) {
            loadingEl.style.display = 'none';
        }
    }
    
    // 显示错误提示
    showError(message) {
        let errorEl = document.getElementById('global-error');
        if (!errorEl) {
            errorEl = document.createElement('div');
            errorEl.id = 'global-error';
            errorEl.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background-color: #fee2e2;
                color: #dc2626;
                padding: 12px 16px;
                border-radius: 8px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                z-index: 9999;
                max-width: 300px;
                font-size: 14px;
                border-left: 4px solid #dc2626;
            `;
            document.body.appendChild(errorEl);
        }
        errorEl.textContent = message;
        errorEl.style.display = 'block';
        
        // 3秒后自动隐藏
        setTimeout(() => {
            errorEl.style.display = 'none';
        }, 3000);
    }
    
    // 显示成功提示
    showSuccess(message) {
        let successEl = document.getElementById('global-success');
        if (!successEl) {
            successEl = document.createElement('div');
            successEl.id = 'global-success';
            successEl.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background-color: #d1fae5;
                color: #065f46;
                padding: 12px 16px;
                border-radius: 8px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                z-index: 9999;
                max-width: 300px;
                font-size: 14px;
                border-left: 4px solid #059669;
            `;
            document.body.appendChild(successEl);
        }
        successEl.textContent = message;
        successEl.style.display = 'block';
        
        // 3秒后自动隐藏
        setTimeout(() => {
            successEl.style.display = 'none';
        }, 3000);
    }
    
    // 处理响应
    async handleResponse(response, endpoint, options) {
        const { responseType = 'json' } = options;
        
        if (!response.ok) {
            // 处理401未授权
            if (response.status === 401) {
                // 尝试刷新令牌
                const refreshed = await AuthService.refreshToken();
                if (refreshed) {
                    // 令牌刷新成功，重新请求
                    return this.request(endpoint, options);
                }
            }
            
            // 处理错误响应
            let errorMessage = `请求失败: ${response.status}`;
            try {
                const data = await response.json();
                if (data.detail) {
                    errorMessage = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
                } 
                else if (data.message) {
                    errorMessage = typeof data.message === 'string' ? data.message : JSON.stringify(data.message);
                }
            } catch (e) {
                // 如果无法解析JSON，使用默认错误信息
            }
            
            throw new Error(errorMessage);
        }
        
        // 根据responseType处理响应数据
        if (responseType === 'blob') {
            return response;
        } else {
            const data = await response.json();
            // 处理响应数据，确保返回data字段中的内容
            console.log(`最终返回数据:`, data.data || data);
            return data.data || data;
        }
    }
    
    // 下载Blob文件
    downloadBlob(response, defaultFilename) {
        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response]));
        const link = document.createElement('a');
        link.href = url;
        
        // 安全地获取文件名
        let fileName = defaultFilename;

        // 检查 response 是否有 headers 属性 (如果是纯 Blob 对象，则没有 headers)
        if (response.headers && typeof response.headers.get === 'function') {
            const contentDisposition = response.headers.get('content-disposition');
            if (contentDisposition) {
                const fileNameMatch = contentDisposition.match(/filename="?([^"\s]+)"?/);
                if (fileNameMatch && fileNameMatch.length > 1) {
                    fileName = fileNameMatch[1];
                }
            }
        }
        
        link.setAttribute('download', fileName);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    }
    
    // 统一的请求方法
    async request(endpoint, options = {}) {
        // 检查当前页面是否为P-GUEST_INTERVIEW.html
        const isGuestInterviewPage = window.location.pathname.includes('guest-interview');
        
        const { 
            method = 'GET', 
            body = null, 
            headers = {}, 
            showLoading = !isGuestInterviewPage, // 嘉宾访谈页面默认不显示加载状态
            responseType = 'json' // 新增responseType选项
        } = options;
        
        // 显示加载状态
        if (showLoading) {
            this.showLoading();
        }
        
        try {
            // 合并请求头
            const mergedHeaders = {
                ...AuthService.getHeaders(),
                ...headers
            };
            
            // 构建请求配置
            const config = {
                method: method,
                headers: mergedHeaders,
                credentials: 'include',
                mode: 'cors'
            };
            
            // 添加请求体
            if (body) {
                config.body = JSON.stringify(body);
            }
            
            // 获取完整URL
            const fullUrl = this.getFullURL(endpoint);
            console.log(`API请求: ${method} ${fullUrl}`);
            console.log(`请求头:`, mergedHeaders);
            console.log(`请求体:`, body);
            console.log(`响应类型:`, responseType);
            
            // 发送请求
            const response = await fetch(fullUrl, config);
            console.log(`API响应状态: ${response.status}`);
            console.log(`API响应头:`, response.headers);
            
            // 处理响应
            const result = await this.handleResponse(response, endpoint, options);
            
            if (responseType === 'blob') {
                // 对于blob类型，返回的是response对象，需要获取blob数据
                // 1. 获取二进制数据
                const blobData = await result.blob();
                
                // 2. 把 Headers 手动挂载到 Blob 对象上
                // 这样 downloadBlob 函数里的 response.headers.get() 才能工作
                blobData.headers = result.headers;
                
                return blobData;
            }
            
            console.log(`API响应数据:`, result);
            return result;
        } catch (error) {
            // 显示错误提示，确保错误信息是字符串
            console.error(`API请求失败:`, error);
            
            // 确保错误信息是字符串
            const errorMessage = error.message || JSON.stringify(error);
            this.showError(errorMessage);
            
            // 确保抛出的错误是Error对象，且信息是字符串
            throw new Error(errorMessage);
        } finally {
            // 隐藏加载状态
            if (showLoading) {
                this.hideLoading();
            }
        }
    }
    
    // GET请求
    async get(endpoint, options = {}) {
        return this.request(endpoint, {
            method: 'GET',
            ...options
        });
    }
    
    // POST请求
    async post(endpoint, body, options = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: body,
            ...options
        });
    }
    
    // PUT请求
    async put(endpoint, body, options = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: body,
            ...options
        });
    }
    
    // DELETE请求
    async delete(endpoint, options = {}) {
        return this.request(endpoint, {
            method: 'DELETE',
            ...options
        });
    }
    
    // PATCH请求
    async patch(endpoint, body, options = {}) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: body,
            ...options
        });
    }
    
    // 导出选中会话
    async exportSelectedSessions(ids, defaultFilename = 'selected_export.xlsx') {
        const response = await this.request('/export/selected', {
            method: 'POST',
            body: { session_ids: ids },
            responseType: 'blob',
            showLoading: true
        });
        
        this.downloadBlob(response, defaultFilename);
        return true;
    }
    
    // 导出项目所有会话
    async exportAllSessions(projectId, defaultFilename = 'all_export.xlsx') {
        const response = await this.request(`/export/project/${projectId}`, {
            method: 'GET',
            responseType: 'blob',
            showLoading: true
        });
        
        this.downloadBlob(response, defaultFilename);
        return true;
    }
    
    // 导出单个会话
    async exportSingleSession(sessionId, defaultFilename = 'single_export.xlsx') {
        const response = await this.request(`/export/session/${sessionId}`, {
            method: 'GET',
            responseType: 'blob',
            showLoading: true
        });
        
        this.downloadBlob(response, defaultFilename);
        return true;
    }
}

// 创建API实例
const apiService = new API();

export default apiService;
export { API };