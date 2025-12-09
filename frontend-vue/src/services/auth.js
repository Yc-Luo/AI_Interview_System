// 统一的认证工具类，与原auth.js保持一致

// 认证工具类
const AuthService = {
    // 不再使用硬编码的API基础URL，所有请求使用相对路径
    
    // 移除API基础URL相关的方法，使用相对路径发送请求
    setApiBaseUrl() {
        // 不再保存API基础URL到localStorage
        localStorage.removeItem('api_base_url');
    },
    
    getApiBaseUrl() {
        // 返回空字符串，让请求使用相对路径
        return '';
    },
    
    // 设置会话信息
    setSession(data) {
        localStorage.setItem('access_token', data.access_token);
        if (data.refresh_token) {
            localStorage.setItem('refresh_token', data.refresh_token);
        }
        localStorage.setItem('user_id', data.user_id);
        localStorage.setItem('username', data.username);
        if (data.expires_at) {
            localStorage.setItem('token_expires_at', data.expires_at);
        }
    },
    
    // 获取访问令牌
    getToken() {
        return localStorage.getItem('access_token');
    },
    
    // 获取刷新令牌
    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    },
    
    // 获取用户名
    getUsername() {
        return localStorage.getItem('username');
    },
    
    // 获取用户ID
    getUserId() {
        return localStorage.getItem('user_id');
    },
    
    // 检查令牌是否过期
    isTokenExpired() {
        const expiresAt = localStorage.getItem('token_expires_at');
        // 如果没有过期时间，默认认为令牌未过期
        if (!expiresAt) return false;
        return new Date().getTime() > parseInt(expiresAt) * 1000;
    },
    
    // 检查是否已登录
    isLoggedIn() {
        return !!this.getToken() && !this.isTokenExpired();
    },
    
    // 刷新令牌
    async refreshToken() {
        try {
            const refreshToken = this.getRefreshToken();
            if (!refreshToken) {
                this.logout();
                return false;
            }
            
            // 使用相对路径发送请求，让请求走代理
            const response = await fetch('/api/auth/refresh', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    refresh_token: refreshToken
                }),
                credentials: 'include',
                mode: 'cors'
            });
            
            if (!response.ok) {
                this.logout();
                return false;
            }
            
            const data = await response.json();
            this.setSession(data.data || data);
            return true;
        } catch (error) {
            console.error('刷新令牌失败:', error);
            this.logout();
            return false;
        }
    },
    
    // 登出
    logout() {
        localStorage.clear();
        // 跳转到登录页面
        window.location.href = '/login';
    },
    
    // 获取请求头
    getHeaders() {
        const token = this.getToken();
        const headers = {
            'Content-Type': 'application/json',
            'X-CSRF-Token': this.getCsrfToken()
        };
        
        // 只有当token存在时才添加Authorization头
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        return headers;
    },
    
    // 生成CSRF令牌
    generateCsrfToken() {
        const token = Math.random().toString(36).substring(2) + Date.now().toString(36);
        localStorage.setItem('csrf_token', token);
        return token;
    },
    
    // 获取CSRF令牌
    getCsrfToken() {
        let token = localStorage.getItem('csrf_token');
        if (!token) {
            token = this.generateCsrfToken();
        }
        return token;
    },
    
    // 验证CSRF令牌
    validateCsrfToken(token) {
        const storedToken = localStorage.getItem('csrf_token');
        return token === storedToken;
    },
    
    // 要求认证
    requireAuth() {
        if (!this.isLoggedIn()) {
            if (window.location.protocol === 'blob:' || window.location.href.includes('scf.usercontent.goog')) {
                // 预览环境模拟登录
                const doMock = confirm("检测到未登录。是否模拟登录状态以便预览？");
                if(doMock) {
                    this.setSession({
                        access_token: 'mock_token',
                        refresh_token: 'mock_refresh_token',
                        user_id: 'mock_user',
                        username: 'PreviewUser',
                        expires_at: Math.floor(Date.now() / 1000) + 3600
                    });
                    window.location.reload();
                }
            } else {
                window.location.href = '/login';
            }
        }
    },
    
    // 清除认证信息
    clearAuth() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('username');
        localStorage.removeItem('token_expires_at');
    }
};

export default AuthService;
