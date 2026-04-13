import { request } from './request'

// 合同状态
export type ContractStatus = 'draft' | 'pending_approval' | 'approved' | 'active' | 'completed' | 'terminated' | 'renewed'

// 合同详情
export interface ContractDetail {
  id: number
  opportunity_id?: number
  opportunity_name?: string
  organization_id: number
  org_name?: string
  contract_number: string
  contract_name: string
  contract_amount: number
  currency: string
  start_date: string
  end_date: string
  duration_months: number
  contract_type: string
  status: ContractStatus
  signed_date: string
  termination_reason: string
  renewal_date: string
  contract_file_url: string
  terms_and_conditions: string
  tags: string[]
  created_at: string
  updated_at: string
}

// 合同列表响应
export interface ContractListResponse {
  items: ContractDetail[]
  total: number
  page: number
  pageSize: number
}

// 合同列表参数
export interface ContractListParams {
  page?: number
  pageSize?: number
  keyword?: string
  org_id?: number
  status?: ContractStatus
  start_date?: string
  end_date?: string
}

// 获取合同列表
export function getContractList(params: ContractListParams) {
  return request.get<ContractListResponse>('/contracts', params)
}

// 获取合同详情
export function getContractDetail(id: number) {
  return request.get<ContractDetail>(`/contracts/${id}`)
}

// 创建合同
export function createContract(data: Partial<ContractDetail>) {
  return request.post('/contracts', data)
}

// 更新合同
export function updateContract(id: number, data: Partial<ContractDetail>) {
  return request.put(`/contracts/${id}`, data)
}

// 删除合同
export function deleteContract(id: number) {
  return request.delete(`/contracts/${id}`)
}

// 更新合同状态
export function updateContractStatus(id: number, status: ContractStatus) {
  return request.post(`/contracts/${id}/status`, { status })
}
