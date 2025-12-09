// 用户状态管理
import { defineStore } from 'pinia'
import AuthService from '../services/auth'
import apiService from '../services/api'

// 定义用户状态管理
const useUserStore = defineStore('user', {
  state: () => ({
    isLoggedIn: AuthService.isLoggedIn(),
    username: AuthService.getUsername(),
    userId: AuthService.getUserId(),
    token: AuthService.getToken(),
    loading: false,
    error: null
  }),
  
  getters: {
    isAuthenticated: (state) => state.isLoggedIn,
    currentUser: (state) => ({
      username: state.username,
      userId: state.userId
    })
  },
  
  actions: {
    // 登录
    async login(credentials) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await apiService.post('/auth/login', credentials);
        AuthService.setSession(response);
        
        // 更新状态
        this.isLoggedIn = true;
        this.username = response.username;
        this.userId = response.user_id;
        this.token = response.access_token;
        
        return response;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    // 注册
    async register(credentials) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await apiService.post('/auth/register', credentials);
        AuthService.setSession(response.data);
        
        // 更新状态
        this.isLoggedIn = true;
        this.username = response.data.username;
        this.userId = response.data.user_id;
        this.token = response.data.access_token;
        
        return response;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    // 登出
    logout() {
      AuthService.logout();
      
      // 重置状态
      this.isLoggedIn = false;
      this.username = null;
      this.userId = null;
      this.token = null;
    },
    
    // 刷新令牌
    async refreshToken() {
      try {
        const refreshed = await AuthService.refreshToken();
        if (refreshed) {
          // 更新状态
          this.isLoggedIn = true;
          this.username = AuthService.getUsername();
          this.userId = AuthService.getUserId();
          this.token = AuthService.getToken();
        } else {
          this.logout();
        }
        return refreshed;
      } catch (error) {
        this.logout();
        throw error;
      }
    },
    
    // 检查登录状态
    checkLoginStatus() {
      const loggedIn = AuthService.isLoggedIn();
      this.isLoggedIn = loggedIn;
      
      if (loggedIn) {
        this.username = AuthService.getUsername();
        this.userId = AuthService.getUserId();
        this.token = AuthService.getToken();
      } else {
        this.username = null;
        this.userId = null;
        this.token = null;
      }
      
      return loggedIn;
    }
  }
});

export default useUserStore;
