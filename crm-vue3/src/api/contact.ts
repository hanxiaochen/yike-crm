import { request } from './request'

// 联系人列表参数
export interface ContactListParams {
  page?: number
  pageSize?: number
  keyword?: string
  org_id?: number
  tags?: string[]
}

// 联系人详情
export interface ContactDetail {
  id: number
  organization_id: number
  org_name?: string
  name: string
  position: string
  phone: string
  email: string
  is_alumni: boolean
  alumni_info: string
  other_info: string
  is_primary: boolean
  tags: string[]
  created_at: string
  updated_at: string
  deals?: any[]
  activities?: any[]
}

// 联系人列表响应
export interface ContactListResponse {
  items: ContactDetail[]
  total: number
  page: number
  pageSize: number
}

// 获取联系人列表
export function getContactList(params: ContactListParams) {
  return request.get<ContactListResponse>('/contacts', params)
}

// 获取联系人详情
export function getContactDetail(id: number) {
  return request.get<ContactDetail>(`/contacts/${id}`)
}

// 创建联系人
export function createContact(data: Partial<ContactDetail>) {
  return request.post('/contacts', data)
}

// 更新联系人
export function updateContact(id: number, data: Partial<ContactDetail>) {
  return request.put(`/contacts/${id}`, data)
}

// 删除联系人
export function deleteContact(id: number) {
  return request.delete(`/contacts/${id}`)
}
