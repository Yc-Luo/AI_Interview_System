// API服务封装

// 默认API基础URL
const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000';

// 请求拦截器
async function requestInterceptor(config) {
  // 从localStorage获取token
  const token = localStorage.getItem('token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
}

// 响应拦截器
async function responseInterceptor(response) {
  return response;
}

// 错误处理
function handleError(error) {
  console.error('API请求失败:', error);
  throw error;
}

// API请求方法
async function request(url, options = {}) {
  try {
    // 构建完整URL
    const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`;
    
    // 处理请求配置
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };
    
    // 请求拦截
    const interceptedConfig = await requestInterceptor(config);
    
    // 发送请求
    const response = await fetch(fullUrl, interceptedConfig);
    
    // 处理响应
    let data;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }
    
    // 检查响应状态
    if (!response.ok) {
      const error = new Error(data.message || `HTTP Error ${response.status}`);
      error.status = response.status;
      error.data = data;
      throw error;
    }
    
    // 响应拦截
    const interceptedResponse = await responseInterceptor(data);
    return interceptedResponse;
  } catch (error) {
    return handleError(error);
  }
}

// 导出API方法
const api = {
  // GET请求
  get: (url, params) => {
    // 处理查询参数
    let fullUrl = url;
    if (params) {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, value);
        }
      });
      const queryString = searchParams.toString();
      if (queryString) {
        fullUrl += (url.includes('?') ? '&' : '?') + queryString;
      }
    }
    return request(fullUrl, { method: 'GET' });
  },
  
  // POST请求
  post: (url, data) => {
    return request(url, { method: 'POST', body: JSON.stringify(data) });
  },
  
  // PUT请求
  put: (url, data) => {
    return request(url, { method: 'PUT', body: JSON.stringify(data) });
  },
  
  // DELETE请求
  delete: (url) => {
    return request(url, { method: 'DELETE' });
  },
  
  // 请求方法
  request,
};

export default api;
export { api };