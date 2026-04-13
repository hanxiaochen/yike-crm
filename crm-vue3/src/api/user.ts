import { request } from './request'

export interface User {
  id: number
  username: string
  name: string
  email: string
  role: number
  role_name?: string
  status: number
  last_login: string
  created_at: string
}

export interface UserQuery {
  page?: number
  pageSize?: number
  keyword?: string
}

export function getUserList(params: UserQuery) {
  return request.get<{ items: User[]; total: number; page: number; pageSize: number }>('/users', { params })
}

export function createUser(data: { username: string; password: string; name: string; email?: string; role?: number; status?: number }) {
  return request.post('/users', data)
}

export function updateUser(userId: number, data: { username?: string; name?: string; email?: string; role?: number; status?: number }) {
  return request.put(`/users/${userId}`, data)
}

export function deleteUser(userId: number) {
  return request.delete(`/users/${userId}`)
}

export function resetUserPassword(userId: number) {
  return request.post(`/users/${userId}/reset-password`, {})
}
