import { request } from './request'

export interface Role {
  id: number
  name: string
  code: string
  description: string
  permissions: Record<string, any>
  is_system?: boolean
  userCount: number
  status: number
}

export function getRoleList() {
  return request.get<{ items: Role[]; total: number }>('/roles')
}

export function updateRolePermissions(roleId: number, permissions: Record<string, any>) {
  return request.put(`/roles/${roleId}/permissions`, { permissions })
}
