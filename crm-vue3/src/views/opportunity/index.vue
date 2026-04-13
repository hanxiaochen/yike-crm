<template>
  <div class="opportunity-page">
    <!-- 主内容区 -->
    <template v-if="!detailMode">
      <div class="search-bar">
        <div class="search-form">
          <el-input
            ref="searchInputRef"
            v-model="query.keyword"
            placeholder="搜索商机名称..."
            clearable
            style="width: 260px"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select v-model="query.stage" placeholder="采购阶段" clearable style="width: 200px" @change="handleSearch">
            <el-option label="① 业务驱动、定位问题" value="business_driven" />
            <el-option label="② 确定需求、启动项目" value="needs_defined" />
            <el-option label="③ 评估方案、圈定供应商" value="evaluation" />
            <el-option label="④ 制定规则、落实采购" value="procurement" />
            <el-option label="⑤ 签订合同" value="contract_signed" />
            <el-option label="⑥ 付款收货、实施评估" value="payment_implementation" />
            <el-option label="赢单" value="closed_won" />
            <el-option label="输单" value="closed_lost" />
          </el-select>
          <el-select v-model="query.priority" placeholder="优先级" clearable style="width: 110px" @change="handleSearch">
          <el-select v-model="query.forecast_category" placeholder="预测" clearable style="width: 100px" @change="handleSearch">
            <el-option label="机会" value="opportunity" />
            <el-option label="可能+" value="possible_plus" />
            <el-option label="可能-" value="possible_minus" />
            <el-option label="优势" value="advantage" />
            <el-option label="确保" value="ensure" />
          </el-select>
            <el-option label="紧急" value="urgent" />
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
          <el-select v-model="query.org_id" placeholder="客户" clearable filterable style="width: 160px" @change="handleSearch">
            <el-option v-for="org in orgOptions" :key="org.id" :label="org.name" :value="org.id" />
          </el-select>
        </div>
        <span class="search-shortcut-hint">按 / 聚焦搜索</span>
        <div class="action-buttons">
          <span v-if="selectedRows.length > 0" class="selected-info">已选择 {{ selectedRows.length }} 项</span>
          <el-button v-if="selectedRows.length > 0" type="danger" @click="handleBatchDelete"><el-icon><Delete /></el-icon>批量删除</el-button>
          <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon>新建商机</el-button>
        </div>
      </div>

      <div v-if="viewMode === 'list'">
        <el-card shadow="never" class="table-card">
          <el-table v-loading="loading" :data="tableData" row-key="id" @selection-change="handleSelectionChange" table-layout="auto" :show-summary="selectedRows.length > 0" :summary-text="''" :summary-method="getSummary">
            <el-table-column type="selection" min-width="50" />
            <el-table-column prop="opportunity_name" label="商机名称" min-width="180" sortable show-overflow-tooltip>
              <template #default="{ row }"><el-link type="primary" @click="handleView(row)"><span class="name-cell">{{ row.opportunity_name }}</span></el-link></template>
            </el-table-column>
            <el-table-column prop="org_name" label="客户" min-width="120" show-overflow-tooltip />
            <el-table-column prop="estimated_amount" label="商机金额" min-width="120">
              <template #default="{ row }"><span style="color:#67c23a;font-weight:600">¥{{ (row.estimated_amount || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span></template>
            </el-table-column>
            <el-table-column prop="stage" label="采购阶段" min-width="180">
              <template #default="{ row }"><el-tag :style="getStageStyle(row.stage)" effect="plain">{{ getStageLabel(row.stage) }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="forecast_category" label="预测类别" min-width="90">
              <template #default="{ row }"><span>{{ getForecastLabel(row.forecast_category) }}</span></template>
            </el-table-column>
            <el-table-column prop="estimated_close_date" label="预计成交" min-width="110">
              <template #default="{ row }"><span :class="{ 'text-danger': isOverdue(row.estimated_close_date) }">{{ formatDate(row.estimated_close_date) }}</span></template>
            </el-table-column>
            <el-table-column prop="assigned_to" label="负责人" min-width="100" show-overflow-tooltip />
            <el-table-column label="操作" min-width="180">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleView(row)"><el-icon><View /></el-icon>查看</el-button>
                <el-button type="primary" link size="small" @click="handleEdit(row)"><el-icon><Edit /></el-icon>编辑</el-button>
                <el-popconfirm title="确定删除该商机？" @confirm="handleDelete(row)"><template #reference><el-button type="danger" link size="small"><el-icon><Delete /></el-icon>删除</el-button></template></el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
          <div class="pagination-container">
            <el-pagination background layout="total, prev, pager, next, sizes, jumper" v-model:current-page="query.page" v-model:page-size="query.pageSize" :total="total" :page-sizes="[10, 20, 50, 100]" @current-change="fetchData" @size-change="handleSizeChange" />
          </div>
        </el-card>
      </div>
      <div v-else><OpportunityKanban /></div>
    </template>

    <template v-if="detailMode">
      <div class="detail-header">
        <el-page-header :content="isEdit ? '编辑商机' : '商机详情'" @back="handleBack" />
        <div class="detail-actions">
          <template v-if="!isEdit"><el-button type="primary" @click="handleEdit(detail!)">编辑</el-button></template>
          <template v-else><el-button @click="handleCancel">取消</el-button><el-button type="primary" @click="handleSave" :loading="submitLoading">保存 <span style="font-size:11px;opacity:0.7;margin-left:4px;">⌘↵</span></el-button><span class="shortcut-hint">ESC 返回</span></template>
        </div>
      </div>

      <el-card shadow="never" style="margin-top: 20px;" v-if="!isEdit && detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="商机名称">{{ detail.opportunity_name }}</el-descriptions-item>
          <el-descriptions-item label="客户">{{ detail.org_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="采购阶段"><el-tag :style="getStageStyle(detail.stage)" effect="plain">{{ getStageLabel(detail.stage) }}</el-tag></el-descriptions-item>
          <el-descriptions-item label="预测类别">{{ getForecastLabel(detail.forecast_category) || '-' }}</el-descriptions-item>
          <el-descriptions-item label="商机金额"><span class="amount-text">¥{{ detail.estimated_amount?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span></el-descriptions-item>
          <el-descriptions-item label="销售预期"><span class="sales-expectation">{{ calcSalesExpectation(detail.estimated_amount, detail.forecast_category) }}</span></el-descriptions-item>
          <el-descriptions-item label="商机来源">{{ detail.source || '-' }}</el-descriptions-item>
          <el-descriptions-item label="预计成交日期">{{ detail.estimated_close_date || '-' }}</el-descriptions-item>
          <el-descriptions-item label="负责人">{{ detail.assigned_to || '-' }}</el-descriptions-item>
          <el-descriptions-item label="商机状态"><el-tag :type="detail.status === 'active' ? 'success' : 'info'" size="small">{{ detail.status === 'active' ? '进行中' : detail.status === 'closed' ? '已关闭' : '已归档' }}</el-tag></el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ detail.created_at }}</el-descriptions-item>
          <el-descriptions-item label="客户需求" :span="2">{{ detail.requirements || '-' }}</el-descriptions-item>
          <el-descriptions-item label="竞争对手">{{ detail.competitors || '-' }}</el-descriptions-item>
          <el-descriptions-item label="备注">{{ detail.description || '-' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 详情内容（带标签页） -->
      <el-tabs v-if="!isEdit && detail" style="margin-top: 20px;">
        <!-- 跟踪记录 Tab -->
        <el-tab-pane label="跟踪记录">
          <el-card shadow="never">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center;"><span>跟踪记录</span><el-button type="primary" size="small" @click="handleSaveFollowup" :loading="followupLoading">保存跟踪记录</el-button></div>
            </template>
            <el-input v-model="followupText" type="textarea" :rows="4" placeholder="请输入跟踪记录内容（支持Markdown格式）" style="margin-bottom: 12px;" />
            <div v-if="followupText" class="followup-preview"><div class="preview-label">预览：</div><div v-html="renderMarkdown(followupText)"></div></div>
            <div v-if="followupRecords.length > 0" class="followup-records">
              <el-divider content-position="center">历史记录</el-divider>
              <div v-for="record in followupRecords" :key="record.id" class="followup-record-item">
                <div class="record-title">{{ record.title }}</div>
                <div class="record-body" v-html="renderMarkdown(record.description)"></div>
                <div class="record-footer">{{ record.recorded_by }} · {{ record.activity_date || record.created_at }}</div>
              </div>
            </div>
          </el-card>
        </el-tab-pane>

        <!-- 操作日志 Tab -->
        <el-tab-pane>
          <template #label>
            <span>操作日志 <el-badge :value="operationLogs.length" :hidden="operationLogs.length === 0" type="warning" /></span>
          </template>
          <el-card shadow="never">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>操作日志</span>
                <el-button type="primary" size="small" @click="fetchOperationLogs" :loading="opLogLoading">刷新</el-button>
              </div>
            </template>
            <div v-if="operationLogs.length > 0" class="operation-logs">
              <el-timeline>
                <el-timeline-item v-for="log in operationLogs" :key="log.id" :timestamp="log.activity_date" placement="top" type="warning">
                  <el-card shadow="never">
                    <div class="log-title">{{ log.title }}</div>
                    <div class="log-body">{{ log.description }}</div>
                    <div class="log-footer">{{ log.recorded_by }} · {{ log.created_at }}</div>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </div>
            <el-empty v-else description="暂无操作日志" />
          </el-card>
        </el-tab-pane>

        <!-- 关联合同 Tab -->
        <el-tab-pane>
          <template #label>
            <span>关联合同 <el-badge :value="contracts.length" :hidden="contracts.length === 0" /></span>
          </template>
          <el-card shadow="never">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>关联合同 ({{ contracts.length }})</span>
                <el-button type="primary" size="small" @click="router.push('/contract')">查看全部合同</el-button>
              </div>
            </template>
            <el-table v-if="contracts.length > 0" :data="contracts" border stripe>
              <el-table-column prop="contract_number" label="合同编号" min-width="150" />
              <el-table-column prop="contract_name" label="合同名称" min-width="200">
                <template #default="{ row }">
                  <el-link type="primary" @click="handleViewContract(row)">{{ row.contract_name }}</el-link>
                </template>
              </el-table-column>
              <el-table-column prop="contract_amount" label="合同金额" min-width="140">
                <template #default="{ row }">
                  ¥{{ row.contract_amount?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" min-width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'active' ? 'success' : row.status === 'draft' ? 'info' : 'warning'" size="small">
                    {{ row.status === 'active' ? '执行中' : row.status === 'draft' ? '草稿' : row.status === 'completed' ? '已完成' : '其他' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="signed_date" label="签订日期" min-width="120" />
              <el-table-column label="操作" min-width="100">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="handleViewContract(row)">详情</el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-else description="暂无关联合同" />
          </el-card>
        </el-tab-pane>
      </el-tabs>

      <el-card shadow="never" style="margin-top: 20px;" v-if="isEdit">
        <el-form ref="formRef" :model="form" label-width="100px">
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="商机名称" required><el-input v-model="form.opportunity_name" placeholder="请输入商机名称" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="客户"><el-select v-model="form.organization_id" placeholder="请选择客户" style="width: 100%; text-align: left;" filterable clearable @change="handleOrgChange"><el-option v-for="org in orgOptions" :key="org.id" :label="org.name" :value="org.id" /></el-select></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="采购阶段"><el-select v-model="form.stage" style="width: 100%; text-align: left;"><el-option label="① 业务驱动、定位问题（10%）" value="business_driven" /><el-option label="② 确定需求、启动项目（30%）" value="needs_defined" /><el-option label="③ 评估方案、圈定供应商（50%）" value="evaluation" /><el-option label="④ 制定规则、落实采购（70%）" value="procurement" /><el-option label="⑤ 得到结果、签订合同（90%）" value="contract_signed" /><el-option label="⑥ 付款收货、实施评估（100%）" value="payment_implementation" /><el-option label="赢单" value="closed_won" /><el-option label="输单" value="closed_lost" /></el-select></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="预测类别"><el-select v-model="form.forecast_category" placeholder="请选择预测类别" style="width: 100%; text-align: left;"><el-option label="机会" value="opportunity" /><el-option label="可能-" value="possible_minus" /><el-option label="可能+" value="possible_plus" /><el-option label="优势" value="advantage" /><el-option label="确保" value="ensure" /></el-select></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="商机金额"><el-input-number v-model="form.estimated_amount" :precision="2" :min="0" :controls="false" placeholder="请输入金额" style="width: 100%; text-align: left;"/></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="销售预期"><el-input :value="salesExpectation" readonly style="width: 100%; text-align: left;" /></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="商机来源"><el-input v-model="form.source" placeholder="请输入商机来源" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="预计成交"><el-date-picker v-model="form.estimated_close_date" type="date" value-format="YYYY-MM-DD" style="width: 100%; text-align: left;" /></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="负责人"><el-input v-model="form.assigned_to" placeholder="请输入负责人" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="商机状态"><el-select v-model="form.status" style="width: 100%; text-align: left;"><el-option label="进行中" value="active" /><el-option label="已关闭" value="closed" /><el-option label="已归档" value="archived" /></el-select></el-form-item></el-col>
          </el-row>
          <el-form-item label="客户需求"><el-input v-model="form.requirements" type="textarea" :rows="3" placeholder="请输入客户需求" /></el-form-item>
          <el-form-item label="竞争对手"><el-input v-model="form.competitors" placeholder="请输入竞争对手信息" /></el-form-item>
          <el-form-item label="备注"><el-input v-model="form.description" type="textarea" :rows="2" placeholder="请输入备注" /></el-form-item>
        </el-form>
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getOpportunityList, getOpportunityDetail, createOpportunity, updateOpportunity, deleteOpportunity, getOpportunityOperationLogs } from '@/api/opportunity'
import { getCustomerList } from '@/api/customer'
import { request } from '@/api/request'
import { useUserStore } from '@/store/user'
import OpportunityKanban from './kanban.vue'
import { Search, Plus, View, Edit, Delete } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()

const viewMode = ref('list')
const detailMode = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)

const query = reactive({ page: 1, pageSize: 20, keyword: '', stage: '', priority: '', forecast_category: '', org_id: '' as any })
const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)
const selectedRows = ref<any[]>([])
const orgOptions = ref<any[]>([])
const detail = ref<any>(null)
const contracts = ref<any[]>([])
const followupText = ref('')
const followupLoading = ref(false)
const followupRecords = ref<any[]>([])
const operationLogs = ref<any[]>([])
const opLogLoading = ref(false)

const editingId = ref<number | null>(null)
const searchInputRef = ref()
const form = reactive<any>({
  opportunity_name: '', organization_id: null, stage: 'business_driven', source: '',
  estimated_amount: 0, probability: 10, estimated_close_date: '', priority: 'medium',
  assigned_to: '', status: 'active', requirements: '', competitors: '', description: '', forecast_category: 'opportunity'
})

const salesExpectation = computed(() => {
  const aMap: Record<string, number> = { opportunity: 0, possible_minus: 0.2, possible_plus: 0.6, advantage: 0.9, ensure: 1 }
  const a = aMap[form.forecast_category] ?? 0
  return '¥' + (form.estimated_amount * a).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
})

const amountDisplay = computed({
  get: () => form.estimated_amount ? Number(form.estimated_amount).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '',
  set: (val: string) => {
    const cleaned = val.replace(/[^\d.]/g, '')
    const num = parseFloat(cleaned)
    form.estimated_amount = isNaN(num) ? 0 : Math.round(num * 100) / 100
  }
})

const stageProbabilityMap: Record<string, number> = {
  business_driven: 10, needs_defined: 30, evaluation: 50, procurement: 70,
  contract_signed: 90, payment_implementation: 100, closed_won: 100, closed_lost: 0
}

watch(() => form.stage, (newStage) => {
  if (stageProbabilityMap[newStage] !== undefined) form.probability = stageProbabilityMap[newStage]
})

// 快捷键：Command/Ctrl + Enter 保存，ESC 返回
function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    e.preventDefault()
    if (detailMode.value) {
      handleBack()
    }
  } else if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
    e.preventDefault()
    if (detailMode.value && isEdit.value) {
      handleSave()
    }
  } else if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) {
    e.preventDefault()
    searchInputRef.value?.focus()
  }
}

async function fetchData() { loading.value = true; try { const data = await getOpportunityList(query); tableData.value = data.items || []; total.value = data.total || 0 } catch (e) { console.error(e) } finally { loading.value = false } }
async function fetchOrgs() { try { const data = await getCustomerList({ page: 1, pageSize: 1000 }); orgOptions.value = data.items || [] } catch (e) { console.error(e) } }
function handleOrgChange(_orgId: number) {}
function handleSelectionChange(val: any[]) { selectedRows.value = val }

function getSummary(param: any) {
  const { columns, data } = param
  if (selectedRows.value.length === 0) return []
  const sum = selectedRows.value.reduce((total: number, r: any) => total + (r.estimated_amount || 0), 0)
  return columns.map((col: any, index: number) => {
    if (index === 3) return '选中 ' + selectedRows.value.length + ' 项，合计: ¥' + sum.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    return ''
  })
}
async function handleBatchDelete() {
  if (!selectedRows.value.length) return
  try { await Promise.all(selectedRows.value.map(r => deleteOpportunity(r.id))); ElMessage.success('删除成功'); selectedRows.value = []; fetchData() } catch (e) { if (e !== 'cancel') console.error(e) }
}
function handleSearch() { query.page = 1; fetchData() }
function handleFilterChange() { query.page = 1; fetchData() }
function handleSizeChange(val: number) { query.pageSize = val; fetchData() }

function handleAdd() {
  editingId.value = null
  Object.assign(form, { opportunity_name: '', organization_id: null, stage: 'business_driven', source: '', estimated_amount: 0, probability: 10, estimated_close_date: '', priority: 'medium', assigned_to: '', status: 'active', requirements: '', competitors: '', description: '', forecast_category: 'opportunity' })
  detailMode.value = true; isEdit.value = true
}

function handleBack() { detailMode.value = false; isEdit.value = false; detail.value = null; fetchData() }

async function handleView(row: any) {
  try { 
    detail.value = await getOpportunityDetail(row.id)
    contracts.value = detail.value.contracts || []
    detailMode.value = true
    isEdit.value = false
    followupRecords.value = detail.value.activities || []
    fetchOperationLogs()
  } catch (e) { ElMessage.error('获取商机详情失败') }
}

function handleEdit(row: any) {
  editingId.value = row.id; detail.value = row; detailMode.value = true
  Object.assign(form, { opportunity_name: row.opportunity_name, organization_id: row.organization_id, stage: row.stage || 'business_driven', source: row.source || '', estimated_amount: row.estimated_amount, probability: row.probability || 10, estimated_close_date: row.estimated_close_date || '', priority: row.priority, assigned_to: row.assigned_to || '', status: row.status || 'active', requirements: row.requirements || '', competitors: row.competitors || '', description: row.description || '', forecast_category: row.forecast_category || '' })
  isEdit.value = true
}

function handleCancel() { if (editingId.value) { isEdit.value = false } else { handleBack() } }

async function handleSave() {
  submitLoading.value = true
  try {
    if (editingId.value) { await updateOpportunity(editingId.value, form); ElMessage.success('更新成功'); detail.value = await getOpportunityDetail(editingId.value) }
    else { await createOpportunity(form); ElMessage.success('创建成功'); handleBack(); return }
    isEdit.value = false
  } catch (e) { ElMessage.error('保存失败') } finally { submitLoading.value = false }
}

async function handleDelete(row: any) { try { await deleteOpportunity(row.id); ElMessage.success('删除成功'); fetchData() } catch (e) { ElMessage.error('删除失败') } }

function handleViewContract(row: any) { router.push('/contract?id=' + row.id) }

async function handleSaveFollowup() {
  if (!followupText.value.trim()) { ElMessage.warning('请输入跟踪记录内容'); return }
  followupLoading.value = true
  try {
    await request.post('/activities', { opportunity_id: detail.value.id, activity_type: 'other', activity_date: new Date().toISOString().slice(0, 19).replace('T', ' '), title: '商机跟踪记录', description: followupText.value, recorded_by: userStore.userInfo?.name || '未知' })
    ElMessage.success('跟踪记录已保存')
    const now = new Date().toISOString().slice(0, 19).replace('T', ' ')
    followupRecords.value.unshift({ id: Date.now(), title: '商机跟踪记录', description: followupText.value, recorded_by: userStore.userInfo?.name || '未知', activity_date: now, created_at: now })
    followupText.value = ''
  } catch (e) { console.error('保存跟踪记录失败', e) } finally { followupLoading.value = false }
}

async function fetchFollowupRecords() {
  if (!detail.value?.id) return
  try { const data = await request.get('/activities', { opportunity_id: detail.value.id, page: 1, pageSize: 50 }); followupRecords.value = (data.items || []).filter((r: any) => r.title?.includes('跟踪记录') && r.opportunity_id === detail.value.id) } catch (e) { console.error('获取跟踪记录失败', e) }
}

async function fetchOperationLogs() {
  if (!detail.value?.id) return
  opLogLoading.value = true
  try {
    const data = await getOpportunityOperationLogs(detail.value.id)
    operationLogs.value = data.items || []
  } catch (e) { console.error('获取操作日志失败', e) } finally { opLogLoading.value = false }
}

function renderMarkdown(text: string): string {
  if (!text) return ''
  return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>').replace(/\n/g, '<br>')
}

function getStageTag(stage: string) { const m: Record<string, string> = { business_driven: 'info', needs_defined: 'primary', evaluation: 'warning', procurement: 'danger', contract_signed: 'success', payment_implementation: 'success', closed_won: 'success', closed_lost: 'info' }; return m[stage] || 'info' }
function getStageStyle(stage: string) { const m: Record<string, string> = { business_driven: 'background:#f4f4f5;color:#909399;border-color:#d3d4d6;', needs_defined: 'background:#ecf5ff;color:#409eff;border-color:#b3d8ff;', evaluation: 'background:#fdf6ec;color:#e6a23c;border-color:#faecd8;', procurement: 'background:#fef0f0;color:#f56c6c;border-color:#fde2e2;', contract_signed: 'background:#f0f9ff;color:#7c3aed;border-color:#ddebf7;', payment_implementation: 'background:#e8f8f5;color:#10b981;border-color:#d1fae5;', closed_won: 'background:#f0f9eb;color:#67c23a;border-color:#c2e7b0;', closed_lost: 'background:#f4f4f5;color:#909399;border-color:#d9d9d9;' }; return m[stage] || '' }
function getStageLabel(stage: string) { const m: Record<string, string> = { business_driven: '① 业务驱动、定位问题（10%）', needs_defined: '② 确定需求、启动项目（30%）', evaluation: '③ 评估方案、圈定供应商（50%）', procurement: '④ 制定规则、落实采购（70%）', contract_signed: '⑤ 得到结果、签订合同（90%）', payment_implementation: '⑥ 付款收货、实施评估（100%）', closed_won: '赢单', closed_lost: '输单' }; return m[stage] || stage }
function getStageColor(stage: string) { const m: Record<string, string> = { business_driven: '#909399', needs_defined: '#409eff', evaluation: '#e6a23c', procurement: '#f56c6c', contract_signed: '#7c3aed', payment_implementation: '#10b981', closed_won: '#67c23a', closed_lost: '#909399' }; return m[stage] || '#409EFF' }
function getPriorityType(p: string) { const m: Record<string, string> = { urgent: 'danger', high: 'warning', medium: '', low: 'info' }; return m[p] || 'info' }
function getPriorityLabel(p: string) { const m: Record<string, string> = { urgent: '紧急', high: '高', medium: '中', low: '低' }; return m[p] || p }
function getForecastLabel(c: string) { const m: Record<string, string> = { opportunity: '机会', possible_minus: '可能-', possible_plus: '可能+', advantage: '优势', ensure: '确保' }; return m[c] || '' }
function calcSalesExpectation(amount: number, category: string) { const aMap: Record<string, number> = { opportunity: 0, possible_minus: 0.2, possible_plus: 0.6, advantage: 0.9, ensure: 1 }; const a = aMap[category] ?? 0; return '¥' + (amount * a).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }
function formatDate(date: string) { if (!date) return '-'; return dayjs(date).format('YYYY-MM-DD') }
function isOverdue(date: string) { if (!date) return false; return dayjs(date).isBefore(dayjs(), 'day') }

onMounted(() => { window.addEventListener('keydown', handleKeydown); fetchOrgs(); fetchData() })

onUnmounted(() => { window.removeEventListener('keydown', handleKeydown) })
</script>

<style scoped lang="scss">
:deep(.el-input-number .el-input__inner) {
  text-align: left !important;
}
.opportunity-page {
  .detail-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;

  :deep(.el-page-header) {
    flex: 1;
    display: flex;
    align-items: center;
  }

  :deep(.el-page-header__content) {
    flex: 1;
  }
}

.detail-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}
.shortcut-hint { font-size: 12px; color: #909399; margin-left: 12px; }
.search-shortcut-hint { font-size: 12px; color: #909399; margin-left: auto; }
.amount-text { color: #E6A23C; font-weight: 600; }
  .sales-expectation { color: #67C23A; font-weight: 700; font-size: 15px; }
  .text-danger { color: #F56C6C; }
  
  // 搜索栏响应式
  .search-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 16px;
    
    .search-form {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      flex: 1;
      
      .el-input, .el-select {
        width: auto !important;
        min-width: 120px;
      }
    }
    
    .action-buttons {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-shrink: 0;
      
      .selected-info {
        color: #606266;
        font-size: 14px;
      }
    }
  }
  
  // 表格响应式
  .table-card {
    width: 100%;
    overflow: hidden;
    
    :deep(.el-table) {
      overflow: hidden;
    }
  }
  
  // 详情页响应式
  .detail-header {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
  }
  
  // 小屏幕适配
  @media screen and (max-width: 1024px) {
    .search-bar {
      .search-form {
        .el-input, .el-select {
          width: 100% !important;
        }
      }
    }
    
    .el-descriptions {
      .el-descriptions__label {
        min-width: 100px;
      }
    }
  }
  
  @media screen and (max-width: 768px) {
    .search-bar {
      flex-direction: column;
      
      .search-form {
        width: 100%;
        
        .el-input, .el-select {
          width: 100% !important;
        }
      }
      
      .action-buttons {
        width: 100%;
        justify-content: flex-start;
      }
    }
    
    .pagination-container {
      justify-content: center;
    }
  }
}
.pagination-container { display: flex; justify-content: flex-end; padding: 16px 0 0; }
.action-buttons { display: flex; align-items: center; gap: 12px; .selected-info { color: #606266; font-size: 14px; } }
.followup-preview { background: #f5f7fa; padding: 12px; border-radius: 4px; font-size: 14px; .preview-label { color: #909399; margin-bottom: 8px; font-size: 12px; } :deep(p) { margin: 4px 0; } :deep(strong) { font-weight: bold; } :deep(em) { font-style: italic; } }
.followup-records { margin-top: 16px; .followup-record-item { padding: 12px 0; border-bottom: 1px solid #ebeef5; &:last-child { border-bottom: none; } .record-title { font-weight: 600; color: #303133; margin-bottom: 8px; } .record-body { color: #606266; font-size: 14px; line-height: 1.6; :deep(p) { margin: 4px 0; } :deep(strong) { font-weight: bold; } :deep(em) { font-style: italic; } } .record-footer { text-align: right; font-size: 12px; color: #909399; margin-top: 8px; } } }
// 禁用标签点击，避免点击标签时触发输入框
:deep(.el-form-item__label) {
  pointer-events: none;
}

// 表格操作按钮保持同一行
:deep(.el-table .el-table-column--操作) {
  .cell {
    white-space: nowrap;
  }
}

// 商机名称超出显示省略号
:deep(.el-table .cell .name-cell) {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.operation-logs {
  .log-title { font-weight: 600; color: #303133; margin-bottom: 8px; }
  .log-body { color: #606266; font-size: 14px; line-height: 1.6; white-space: pre-wrap; }
  .log-footer { text-align: right; font-size: 12px; color: #909399; margin-top: 8px; }
}
</style>
