import { defineStore } from 'pinia'
import { login as loginApi, getUserInfo as getUserInfoApi } from '@/api/auth'
import type { LoginParams, LoginResponse } from '@/api/auth'

interface UserInfo {
  id: number
  username: string
  name: string
  email: string
  avatar: string
  role: string
  roleName: string
}

interface UserState {
  token: string
  userInfo: UserInfo | null
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: localStorage.getItem('crm_token') || '',
    userInfo: null
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    userName: (state) => state.userInfo?.name || '用户'
  },

  actions: {
    // 登录
    async login(params: LoginParams) {
      const res = await loginApi(params)
      this.token = res.token
      this.userInfo = res.userInfo
      localStorage.setItem('crm_token', res.token)
      localStorage.setItem('crm_user', JSON.stringify(res.userInfo))
      return res
    },

    // 获取用户信息
    async getUserInfo() {
      if (!this.token) return null
      try {
        const res = await getUserInfoApi()
        this.userInfo = res
        localStorage.setItem('crm_user', JSON.stringify(res))
        return res
      } catch (error) {
        this.token = ''
        this.userInfo = null
        localStorage.removeItem('crm_token')
        localStorage.removeItem('crm_user')
        return null
      }
    },

    // 登出
    logout() {
      // 清除本地状态
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('crm_token')
      localStorage.removeItem('crm_user')
    },
    
    // 仅清除token（不跳转），用于401时防止循环请求
    clearToken() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('crm_token')
      localStorage.removeItem('crm_user')
    },

    // 从本地存储恢复状态
    restoreSession() {
      const token = localStorage.getItem('crm_token')
      const userStr = localStorage.getItem('crm_user')
      if (token) {
        this.token = token
        if (userStr) {
          try {
            this.userInfo = JSON.parse(userStr)
          } catch (e) {
            // 忽略解析错误
          }
        }
      }
    }
  }
})
