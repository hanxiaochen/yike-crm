<template>
  <div class="customer-detail-page">
    <div class="detail-header">
      <el-page-header :content="pageTitle" @back="handleBack">
        <template #extra>
          <el-button v-if="!isEdit && !isNew" type="primary" @click="startEditFromDetail"><el-icon><Edit /></el-icon>编辑</el-button>
          <template v-if="isEdit">
            <el-button @click="handleBack">取消</el-button>
            <el-button type="primary" @click="handleSave" :loading="saveLoading">保存 <span style="font-size:11px;opacity:0.7;margin-left:4px;">⌘↵</span></el-button>
            <span class="shortcut-hint">ESC 返回</span>
          </template>
        </template>
      </el-page-header>
    </div>

    <el-card v-if="isEdit || isNew" shadow="never" style="margin-top: 20px;">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12"><el-form-item label="客户名称" prop="name"><el-input v-model="form.name" placeholder="请输入客户名称" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="客户类型"><el-select v-model="form.type" style="width:100%"><el-option label="最终客户" value="final_customer" /><el-option label="合作伙伴" value="partner" /></el-select></el-form-item></el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12"><el-form-item label="所属行业"><el-select v-model="form.industry" placeholder="请选择行业" style="width:100%"><el-option v-for="ind in industryOptions" :key="ind" :label="ind" :value="ind" /></el-select></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="联系电话"><el-input v-model="form.phone" placeholder="请输入电话" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12"><el-form-item label="电子邮箱"><el-input v-model="form.email" placeholder="请输入邮箱" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="客户地址"><el-input v-model="form.address" placeholder="请输入地址" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="详细描述"><el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入详细描述" /></el-form-item>
        <el-divider content-position="center">开票信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12"><el-form-item label="抬头"><el-input v-model="form.invoice_info" placeholder="请输入发票抬头" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="税号"><el-input v-model="form.tax_number" placeholder="请输入税号" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12"><el-form-item label="开户行"><el-input v-model="form.bank_name" placeholder="请输入开户行" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="银行账号"><el-input v-model="form.bank_account" placeholder="请输入银行账号" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12"><el-form-item label="地址"><el-input v-model="form.invoice_address" placeholder="请输入发票地址" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="电话"><el-input v-model="form.invoice_phone" placeholder="请输入发票电话" /></el-form-item></el-col>
        </el-row>
      </el-form>
    </el-card>

    <template v-if="!isEdit && !isNew && detail">
      <el-card shadow="never" style="margin-top: 20px;">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="客户名称">{{ detail.name }}</el-descriptions-item>
          <el-descriptions-item label="客户类型">{{ getTypeLabel(detail.type) }}</el-descriptions-item>
          <el-descriptions-item label="所属行业">{{ detail.industry || '-' }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ detail.phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="电子邮箱">{{ detail.email || '-' }}</el-descriptions-item>
          <el-descriptions-item label="客户地址">{{ detail.address || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ detail.created_at }}</el-descriptions-item>
          <el-descriptions-item label="详细描述" :span="2">{{ detail.description || '-' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card shadow="never" style="margin-top: 20px;">
        <template #header>
          <span>开票信息</span>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="抬头">{{ detail.invoice_info || '-' }}</el-descriptions-item>
          <el-descriptions-item label="税号">{{ detail.tax_number || '-' }}</el-descriptions-item>
          <el-descriptions-item label="开户行">{{ detail.bank_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="银行账号">{{ detail.bank_account || '-' }}</el-descriptions-item>
          <el-descriptions-item label="地址">{{ detail.invoice_address || '-' }}</el-descriptions-item>
          <el-descriptions-item label="电话">{{ detail.invoice_phone || '-' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-tabs style="margin-top: 20px;">
        <el-tab-pane>
          <template #label><span>跟踪记录 <el-badge :value="followupRecords.length" :hidden="followupRecords.length === 0" /></span></template>
          <el-card shadow="never">
            <template #header>
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <span>跟踪记录</span>
                <el-button type="primary" size="small" @click="handleSaveFollowup" :loading="followupLoading">保存跟踪记录</el-button>
              </div>
            </template>
            <el-input v-model="followupText" type="textarea" :rows="4" placeholder="请输入跟踪记录内容（支持Markdown格式）" style="margin-bottom:12px;" />
            <div v-if="followupText" class="followup-preview">
              <div class="preview-label">预览：</div>
              <div v-html="renderMarkdown(followupText)"></div>
            </div>
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
        <el-tab-pane>
          <template #label><span>联系人 <el-badge :value="contacts.length" :hidden="contacts.length === 0" /></span></template>
          <div style="margin-bottom:12px;text-align:right;">
            <el-button type="primary" size="small" @click="handleAddContact">添加联系人</el-button>
          </div>
          <el-table :data="contacts" border stripe>
            <el-table-column prop="name" label="姓名" min-width="120">
              <template #default="{row}"><el-link type="primary" @click="router.push('/customer/contact?id=' + row.id)">{{ row.name }}</el-link></template>
            </el-table-column>
            <el-table-column prop="department" label="部门" min-width="120" />
            <el-table-column prop="position" label="职位" min-width="120" />
            <el-table-column prop="phone" label="电话" min-width="150" />
            <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
            <el-table-column prop="is_primary" label="主联系人" min-width="100">
              <template #default="{row}"><el-tag v-if="row.is_primary" type="success" size="small">是</el-tag><span v-else>-</span></template>
            </el-table-column>
            <el-table-column label="操作" min-width="100">
              <template #default="{row}"><el-button type="primary" link size="small" @click="router.push('/customer/contact?id=' + row.id)">编辑</el-button></template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane>
          <template #label><span>商机 <el-badge :value="opportunities.length" :hidden="opportunities.length === 0" /></span></template>
          <div style="margin-bottom:12px;text-align:right;">
            <el-button type="primary" size="small" @click="handleAddOpportunity">添加商机</el-button>
          </div>
          <el-table :data="opportunities" border stripe>
            <el-table-column prop="opportunity_name" label="商机名称" min-width="200" />
            <el-table-column prop="estimated_amount" label="金额" min-width="130" />
            <el-table-column prop="stage" label="阶段" min-width="120" />
            <el-table-column prop="probability" label="概率" min-width="80" />
            <el-table-column prop="priority" label="优先级" min-width="80" />
            <el-table-column prop="assigned_to" label="负责人" min-width="100" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane>
          <template #label><span>合同 <el-badge :value="contracts.length" :hidden="contracts.length === 0" /></span></template>
          <div style="margin-bottom:12px;text-align:right;">
            <el-button type="primary" size="small" @click="router.push('/contract')">查看全部合同</el-button>
          </div>
          <el-table :data="contracts" border stripe>
            <el-table-column prop="contract_name" label="合同名称" min-width="200" />
            <el-table-column prop="contract_amount" label="金额" min-width="130" />
            <el-table-column prop="status" label="状态" min-width="100" />
            <el-table-column prop="signed_date" label="签订日期" min-width="120" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane>
          <template #label><span>活动记录 <el-badge :value="activities.length" :hidden="activities.length === 0" /></span></template>
          <div style="margin-bottom:12px;text-align:right;">
            <el-button type="primary" size="small" @click="handleAddActivity">添加活动</el-button>
          </div>
          <el-table :data="activities" border stripe>
            <el-table-column prop="activity_type" label="类型" min-width="100" />
            <el-table-column prop="title" label="标题" min-width="200" />
            <el-table-column prop="activity_date" label="日期" min-width="120" />
            <el-table-column prop="recorded_by" label="记录人" min-width="100" />
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </template>
  </div>
</template>


<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getCustomerDetail, updateCustomer, createCustomer } from '@/api/customer'
import { getContactList } from '@/api/contact'
import { getOpportunityList } from '@/api/opportunity'
import { getContractList } from '@/api/contract'
import { request } from '@/api/request'
import { useUserStore } from '@/store/user'
import { Edit } from '@element-plus/icons-vue'

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()

const detail = ref<any>(null)
const contacts = ref<any[]>([])
const opportunities = ref<any[]>([])
const contracts = ref<any[]>([])
const activities = ref<any[]>([])
const followupText = ref('')
const followupLoading = ref(false)
const followupRecords = ref<any[]>([])
const isEdit = ref(false)
const isNew = ref(false)
const saveLoading = ref(false)
const formRef = ref()

const pageTitle = computed(() => {
  if (isNew.value || isEdit.value) return isNew.value ? '新建客户' : '编辑客户'
  return '客户详情'
})

const form = reactive({
  name: '', type: 'final_customer', industry: '能源', scale: 'medium', phone: '', email: '', address: '',
  potential_score: 0, classification: '', notes: '', description: '',
  invoice_info: '', tax_number: '', bank_name: '', bank_account: '', invoice_address: '', invoice_phone: ''
})

const rules = { name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }] }
const industryOptions = ['能源', '电力', '政府', '金融', '医疗', '教育', '制造业', '互联网', '其他']

// 快捷键：Command/Ctrl + Enter 保存，ESC 返回
function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    e.preventDefault()
    handleBack()
  } else if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
    e.preventDefault()
    if (isEdit.value || isNew.value) {
      handleSave()
    }
  }
}

onMounted(async () => {
  window.addEventListener('keydown', handleKeydown)
  const id = route.params.id
  const action = route.query.action
  if (!id || id === 'new') {
    isNew.value = true
    isEdit.value = true
  } else {
    try {
      detail.value = await getCustomerDetail(Number(id))
      await fetchContacts(Number(id))
      await fetchOpportunities(Number(id))
      await fetchContracts(Number(id))
      await fetchFollowupRecords()
      if (action === 'edit') {
        startEditFromDetail()
      }
    } catch (error) { console.error('获取客户详情失败', error) }
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})

function handleBack() {
  if (isNew.value) { router.back() }
  else if (isEdit.value) { isEdit.value = false }
  else { router.back() }
}

function startEditFromDetail() {
  if (detail.value) {
    Object.assign(form, {
      name: detail.value.name || '',
      type: detail.value.type || '',
      industry: detail.value.industry || '',
      scale: detail.value.scale || '',
      phone: detail.value.phone || '',
      email: detail.value.email || '',
      address: detail.value.address || '',
      potential_score: detail.value.potential_score || 0,
      classification: detail.value.classification || '',
      notes: detail.value.notes || '',
      description: detail.value.description || '',
      invoice_info: detail.value.invoice_info || '',
      tax_number: detail.value.tax_number || '',
      bank_name: detail.value.bank_name || '',
      bank_account: detail.value.bank_account || '',
      invoice_address: detail.value.invoice_address || '',
      invoice_phone: detail.value.invoice_phone || ''
    })
  }
  isEdit.value = true
}

async function handleSave() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    saveLoading.value = true
    try {
      if (isNew.value) {
        await createCustomer(form)
        ElMessage.success('创建成功')
        router.back()
      } else {
        await updateCustomer(Number(route.params.id), form)
        ElMessage.success('更新成功')
        detail.value = await getCustomerDetail(Number(route.params.id))
        isEdit.value = false
      }
    } catch (error) {
      ElMessage.error('保存失败')
    } finally {
      saveLoading.value = false
    }
  })
}

function handleAddContact() { router.push('"') }
function handleAddOpportunity() { router.push('"') }
function handleAddActivity() { router.push('"') }

async function fetchContacts(orgId: number) {
  try {
    const data = await getContactList({ org_id: orgId, page: 1, pageSize: 100 })
    contacts.value = data.items || []
  } catch (error) { console.error('获取联系人列表失败', error) }
}

async function fetchOpportunities(orgId: number) {
  try {
    const data = await getOpportunityList({ org_id: orgId, page: 1, pageSize: 100 })
    opportunities.value = data.items || []
  } catch (error) { console.error('获取商机列表失败', error) }
}

async function fetchContracts(orgId: number) {
  try {
    const data = await getContractList({ org_id: orgId, page: 1, pageSize: 100 })
    contracts.value = data.items || []
  } catch (error) { console.error('获取合同列表失败', error) }
}

async function fetchFollowupRecords() {
  if (!detail.value?.id) return
  try {
    const data = await request.get('/activities', { organization_id: detail.value.id, page: 1, pageSize: 50 })
    followupRecords.value = (data.items || []).filter((r: any) =>
      r.title?.includes('跟踪记录') && !r.contact_id && !r.opportunity_id && !r.contract_id && !r.invoice_id
    )
  } catch (error) { console.error('获取跟踪记录失败', error) }
}

async function handleSaveFollowup() {
  if (!followupText.value.trim()) { ElMessage.warning('请输入跟踪记录内容'); return }
  followupLoading.value = true
  try {
    await request.post('/activities', {
      organization_id: detail.value.id,
      activity_type: 'other',
      activity_date: new Date().toISOString().slice(0, 19).replace('T', ' '),
      title: '客户跟踪记录',
      description: followupText.value,
      recorded_by: userStore.userInfo?.name || '未知'
    })
    ElMessage.success('跟踪记录已保存')
    const now = new Date().toISOString().slice(0, 19).replace('T', ' ')
    followupRecords.value.unshift({ id: Date.now(), title: '客户跟踪记录', description: followupText.value, recorded_by: userStore.userInfo?.name || '未知', activity_date: now, created_at: now })
    followupText.value = ''
  } catch (error) { console.error('保存跟踪记录失败', error) }
  finally { followupLoading.value = false }
}

function renderMarkdown(text: string): string {
  if (!text) return ''
  return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>').replace(/\n/g, '<br>')
}

function getTypeLabel(type: string) {
  const map: Record<string, string> = { final_customer: '最终客户', partner: '合作伙伴' }
  return map[type] || type
}

function getClassificationLabel(c: string) {
  const map: Record<string, string> = { A: 'A类', B: 'B类', C: 'C类', D: 'D类' }
  return map[c] || c
}
</script>


<style scoped lang="scss">
.customer-detail-page {
  .detail-header { margin-bottom: 20px; }
  .shortcut-hint {
    font-size: 12px;
    color: #909399;
    margin-left: 12px;
  }
  // 禁用标签点击，避免点击标签时触发输入框
  :deep(.el-form-item__label) {
    pointer-events: none;
  }
}
.followup-preview {
  background: #f5f7fa; padding: 12px; border-radius: 4px; font-size: 14px;
  .preview-label { color: #909399; margin-bottom: 8px; font-size: 12px; }
  :deep(p) { margin: 4px 0; } :deep(strong) { font-weight: bold; } :deep(em) { font-style: italic; }
}
.followup-records {
  margin-top: 16px;
  .followup-record-item {
    padding: 12px 0; border-bottom: 1px solid #ebeef5;
    &:last-child { border-bottom: none; }
    .record-title { font-weight: 600; color: #303133; margin-bottom: 8px; }
    .record-body { color: #606266; font-size: 14px; line-height: 1.6; :deep(p) { margin: 4px 0; } :deep(strong) { font-weight: bold; } :deep(em) { font-style: italic; } }
    .record-footer { text-align: right; font-size: 12px; color: #909399; margin-top: 8px; }
  }
}
:deep(.el-table .el-table__header .el-table-column--操作 .cell),
:deep(.el-table .el-table__body .el-table-column--操作 .cell) {
  white-space: nowrap;
}
</style>
