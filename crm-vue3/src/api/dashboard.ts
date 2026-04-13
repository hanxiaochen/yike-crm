import { request } from './request'

// 仪表盘统计数据
export interface DashboardStats {
  organizations: number
  contacts: number
  deals: number
  deal_amount: number
  contracts: number
  contract_amount: number
  followup_count: number
  new_insights: number
  // 环比增长
  growth?: {
    organizations?: number
    contacts?: number
    deals?: number
    deal_amount?: number
  }
}

// 商机阶段统计
export interface DealStageStats {
  stage: string
  count: number
  amount: number
}

// 跟进待办
export interface FollowupTodo {
  id: number
  title: string
  type: string
  org_id: number
  org_name: string
  contact_id?: number
  contact_name?: string
  due_date: string
  priority: 'low' | 'medium' | 'high'
  done: boolean
  created_at: string
}

// 近期活动
export interface RecentActivity {
  id: number
  type: string
  title: string
  description: string
  contact_name: string
  org_name: string
  date: string
}

// AI洞察
export interface AIInsight {
  id: number
  insight_type: string
  title: string
  content: string
  priority: 'low' | 'medium' | 'high'
  status: 'new' | 'read' | 'actioned'
  created_at: string
}

// 仪表盘响应
export interface DashboardResponse {
  stats: DashboardStats
  deals_by_stage: DealStageStats[]
  upcoming_followups: FollowupTodo[]
  recent_activities: RecentActivity[]
  recent_insights: AIInsight[]
  funnel_data: { name: string; value: number }[]
  trend_data: { date: string; value: number }[]
}

// 获取仪表盘数据
export function getDashboard() {
  return request.get<DashboardResponse>('/dashboard')
}

// 获取统计数据
export function getStats() {
  return request.get<DashboardStats>('/dashboard/stats')
}

// 获取商机阶段分布
export function getDealStageStats() {
  return request.get<DealStageStats[]>('/dashboard/deal-stats')
}

// 获取待办列表
export function getUpcomingFollowups() {
  return request.get<FollowupTodo[]>('/dashboard/followups')
}

// 更新待办状态
export function updateFollowupStatus(id: number, done: boolean) {
  return request.post(`/dashboard/followups/${id}`, { done })
}

// 获取AI洞察
export function getAIInsights() {
  return request.get<AIInsight[]>('/dashboard/insights')
}
