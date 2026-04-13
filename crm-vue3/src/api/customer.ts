import { request } from './request'

// 客户列表参数
export interface CustomerListParams {
  page?: number
  pageSize?: number
  keyword?: string
  type?: string
  industry?: string
  classification?: string
  sortField?: string
  sortOrder?: 'asc' | 'desc'
}

// 客户详情
export interface CustomerDetail {
  id: number
  name: string
  type: 'final_customer' | 'partner' | 'undecided'
  industry: string
  scale: 'small' | 'medium' | 'large' | 'enterprise'
  address: string
  phone: string
  email: string
  invoice_info: string
  tax_number: string
  bank_account: string
  potential_score: number
  classification: string
  tags: string[]
  created_at: string
  updated_at: string
  created_by: string
  notes: string
  contact_count?: number
  opportunity_count?: number
  contract_count?: number
  last_followup_date?: string
}

// 客户列表响应
export interface CustomerListResponse {
  items: CustomerDetail[]
  total: number
  page: number
  pageSize: number
}

// 获取客户列表
export function getCustomerList(params: CustomerListParams) {
  return request.get<CustomerListResponse>('/customers', params)
}

// 获取客户详情
export function getCustomerDetail(id: number) {
  return request.get<CustomerDetail>(`/customers/${id}`)
}

// 创建客户
export function createCustomer(data: Partial<CustomerDetail>) {
  return request.post('/customers', data)
}

// 更新客户
export function updateCustomer(id: number, data: Partial<CustomerDetail>) {
  return request.put(`/customers/${id}`, data)
}

// 删除客户
export function deleteCustomer(id: number) {
  return request.delete(`/customers/${id}`)
}

// 批量删除客户
export function batchDeleteCustomers(ids: number[]) {
  return request.post('/customers/batch-delete', { ids })
}

// 转移客户
export function transferCustomer(id: number, newOwner: string) {
  return request.post(`/customers/${id}/transfer`, { newOwner })
}

// 获取客户下的联系人
export function getCustomerContacts(customerId: number) {
  return request.get(`/customers/${customerId}/contacts`)
}

// 获取客户下的商机
export function getCustomerOpportunities(customerId: number) {
  return request.get(`/customers/${customerId}/opportunities`)
}

// 获取客户下的合同
export function getCustomerContracts(customerId: number) {
  return request.get(`/customers/${customerId}/contracts`)
}

// 获取客户下的活动
export function getCustomerActivities(customerId: number) {
  return request.get(`/customers/${customerId}/activities`)
}
