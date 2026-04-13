import { request } from './request'

// 发票列表参数
export interface InvoiceListParams {
  page?: number
  pageSize?: number
  keyword?: string
  status?: string
  contract_id?: number
}

// 发票详情
export interface InvoiceDetail {
  id: number
  invoice_number: string
  contract_id?: number
  contract_name?: string
  contract_number?: string
  organization_id: number
  org_name?: string
  invoice_type: string
  amount: number
  tax_rate: number
  tax_amount: number
  total_amount: number
  billing_date: string
  due_date: string
  status: 'draft' | 'issued' | 'paid' | 'void' | 'refund'
  payment_status: 'unpaid' | 'partial' | 'paid'
  paid_amount: number
  notes: string
  created_at: string
  updated_at: string
}

// 发票列表响应
export interface InvoiceListResponse {
  items: InvoiceDetail[]
  total: number
  page: number
  pageSize: number
}

// 获取发票列表
export function getInvoiceList(params: InvoiceListParams) {
  return request.get<InvoiceListResponse>('/invoices', params)
}

// 获取发票详情
export function getInvoiceDetail(id: number) {
  return request.get<InvoiceDetail>(`/invoices/${id}`)
}

// 创建发票
export function createInvoice(data: Partial<InvoiceDetail>) {
  return request.post('/invoices', data)
}

// 更新发票
export function updateInvoice(id: number, data: Partial<InvoiceDetail>) {
  return request.put(`/invoices/${id}`, data)
}

// 删除发票
export function deleteInvoice(id: number) {
  return request.delete(`/invoices/${id}`)
}

// 获取合同下的发票列表
export function getContractInvoices(contractId: number) {
  return request.get<InvoiceListResponse>(`/contracts/${contractId}/invoices`)
}

// 获取发票操作日志
export function getInvoiceOperationLogs(invoiceId: number) {
  return request.get(`/invoices/${invoiceId}/operation-logs`)
}
