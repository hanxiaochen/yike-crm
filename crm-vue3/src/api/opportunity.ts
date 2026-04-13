import { request } from './request'

// 商机阶段
export type OpportunityStage = 'business_driven' | 'needs_defined' | 'evaluation' | 'procurement' | 'contract_signed' | 'payment_implementation' | 'closed_won' | 'closed_lost'

// 预测类别
export type ForecastCategory = 'opportunity' | 'possible_minus' | 'possible_plus' | 'advantage' | 'ensure'

// 商机详情
export interface OpportunityDetail {
  id: number
  organization_id: number
  org_name?: string
  opportunity_name: string
  source: string
  stage: OpportunityStage
  estimated_amount: number
  estimated_close_date: string
  probability: number
  priority: 'low' | 'medium' | 'high' | 'urgent'
  assigned_to: string
  tags: string[]
  description: string
  requirements: string
  competitors: string
  win_reason: string
  loss_reason: string
  closed_date: string
  status: 'active' | 'closed' | 'archived'
  forecast_category: ForecastCategory
  created_at: string
  updated_at: string
}

// 商机列表响应
export interface OpportunityListResponse {
  items: OpportunityDetail[]
  total: number
  page: number
  pageSize: number
}

// 商机列表参数
export interface OpportunityListParams {
  page?: number
  pageSize?: number
  keyword?: string
  org_id?: number
  stage?: OpportunityStage
  priority?: string
  assigned_to?: string
  status?: string
  sortField?: string
  sortOrder?: 'asc' | 'desc'
}

// 获取商机列表
export function getOpportunityList(params: OpportunityListParams) {
  return request.get<OpportunityListResponse>('/opportunities', params)
}

// 获取商机详情
export function getOpportunityDetail(id: number) {
  return request.get<OpportunityDetail>(`/opportunities/${id}`)
}

// 创建商机
export function createOpportunity(data: Partial<OpportunityDetail>) {
  return request.post('/opportunities', data)
}

// 更新商机
export function updateOpportunity(id: number, data: Partial<OpportunityDetail>) {
  return request.put(`/opportunities/${id}`, data)
}

// 删除商机
export function deleteOpportunity(id: number) {
  return request.delete(`/opportunities/${id}`)
}

// 更新商机阶段
export function updateOpportunityStage(id: number, stage: OpportunityStage) {
  return request.post(`/opportunities/${id}/stage`, { stage })
}

// 获取商机活动记录
export function getOpportunityActivities(opportunityId: number) {
  return request.get(`/opportunities/${opportunityId}/activities`)
}

// 添加商机活动
export function addOpportunityActivity(opportunityId: number, data: any) {
  return request.post(`/opportunities/${opportunityId}/activities`, data)
}

// 获取商机操作日志
export function getOpportunityOperationLogs(opportunityId: number) {
  return request.get(`/opportunities/${opportunityId}/operation-logs`)
}
