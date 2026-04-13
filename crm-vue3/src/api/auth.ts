import { request } from './request'

// 登录参数
export interface LoginParams {
  username: string
  password: string
}

// 登录响应
export interface LoginResponse {
  token: string
  userInfo: {
    id: number
    username: string
    name: string
    email: string
    avatar: string
    role: string
    roleName: string
  }
}

// 登录
export function login(data: LoginParams) {
  return request.post<LoginResponse>('/auth/login', data)
}

// 登出
export function logout() {
  return request.post('/auth/logout')
}

// 获取用户信息
export function getUserInfo() {
  return request.get<LoginResponse['userInfo']>('/auth/userinfo')
}

// 修改密码
export function updatePassword(data: { oldPassword: string; newPassword: string }) {
  return request.post('/auth/update-password', data)
}
