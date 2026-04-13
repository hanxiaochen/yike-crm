<template>
  <div class="customer-page">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <div class="search-form">
        <el-input
          ref="searchInputRef"
          v-model="query.keyword"
          placeholder="搜索客户名称/行业..."
          clearable
          style="width: 260px"
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select v-model="query.type" placeholder="客户类型" clearable style="width: 140px" @change="handleSearch">
          <el-option label="最终客户" value="final_customer" />
          <el-option label="合作伙伴" value="partner" />
          <el-option label="待定" value="undecided" />
        </el-select>
        
        <el-select v-model="query.industry" placeholder="所属行业" clearable style="width: 140px" @change="handleSearch">
          <el-option v-for="item in industryOptions" :key="item" :label="item" :value="item" />
        </el-select>
      </div>
      <span class="search-shortcut-hint">按 / 聚焦搜索</span>
      
      <div class="action-buttons">
        <span v-if="selectedRows.length > 0" class="selected-info">
          已选择 {{ selectedRows.length }} 项
        </span>
        <el-button
          v-if="selectedRows.length > 0"
          type="danger"
          @click="handleBatchDelete"
        >
          <el-icon><Delete /></el-icon>
          批量删除
        </el-button>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新建客户
        </el-button>
      </div>
    </div>

    <!-- 表格 -->
    <el-card shadow="never" class="table-card">
      <el-table
        ref="tableRef"
        v-loading="loading"
        :data="tableData"
        row-key="id"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" min-width="50" />
        
        <el-table-column label="客户名称" prop="name" min-width="200" sortable>
          <template #default="{ row }">
            <div class="customer-name-cell">
              <el-link type="primary" @click="router.push(`/customer/detail/${row.id}`)">
                {{ row.name }}
              </el-link>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="类型" prop="type" min-width="80">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)" size="small">
              {{ getTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="行业" prop="industry" min-width="100" />
        
        <el-table-column label="联系人" prop="contact_count" min-width="70">
          <template #default="{ row }">
            <el-link type="primary" @click="handleViewContacts(row)">
              {{ row.contact_count || 0 }}人
            </el-link>
          </template>
        </el-table-column>
        
        <el-table-column label="商机" prop="opportunity_count" min-width="70">
          <template #default="{ row }">
            <el-link type="primary" @click="handleViewOpportunities(row)">
              {{ row.opportunity_count || 0 }}个
            </el-link>
          </template>
        </el-table-column>
        
        <el-table-column label="最近跟进" prop="last_followup_date" min-width="110">
          <template #default="{ row }">
            <span :class="{ 'text-danger': isOverdue(row.last_followup_date) }">
              {{ formatDate(row.last_followup_date) }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" min-width="180">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="router.push(`/customer/detail/${row.id}`)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button type="primary" link size="small" @click="router.push(`/customer/detail/${row.id}?action=edit`)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-popconfirm title="确定删除该客户？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button type="danger" link size="small">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <div class="selection-info">
          <span>已选择 {{ selection.length }} 项</span>
        </div>
        <el-pagination
          background
          layout="total, prev, pager, next, sizes, jumper"
          v-model:current-page="query.page"
          v-model:page-size="query.pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          @current-change="fetchData"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <!-- 新建/编辑抽屉 -->
    <el-drawer
      v-model="dialogVisible"
      :title="editingId ? '编辑客户' : '新建客户'"
      size="700px"
      :close-on-click-modal="false"
      @close="handleDialogClose"
    >
      <div class="drawer-form">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="100px"
          class="customer-form"
        >
          <el-divider content-position="center">基本信息</el-divider>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="客户名称" prop="name">
                <el-input v-model="form.name" placeholder="请输入客户名称" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="客户类型" prop="type">
                <el-select v-model="form.type" placeholder="请选择" style="width: 100%">
                  <el-option label="最终客户" value="final_customer" />
                  <el-option label="合作伙伴" value="partner" />
                  <el-option label="待定" value="undecided" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="所属行业" prop="industry">
                <el-select v-model="form.industry" placeholder="请选择" style="width: 100%" allow-create filterable>
                  <el-option v-for="item in industryOptions" :key="item" :label="item" :value="item" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="企业规模">
                <el-select v-model="form.scale" placeholder="请选择" style="width: 100%">
                  <el-option label="小型" value="small" />
                  <el-option label="中型" value="medium" />
                  <el-option label="大型" value="large" />
                  <el-option label="企业" value="enterprise" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="联系电话">
                <el-input v-model="form.phone" placeholder="请输入电话" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="电子邮箱">
                <el-input v-model="form.email" placeholder="请输入邮箱" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="公司地址">
                <el-input v-model="form.address" placeholder="请输入详细地址" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="潜力评分">
                <el-rate v-model="form.potential_score" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="备注">
                <el-input v-model="form.notes" placeholder="请输入备注" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="简介">
            <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入简介（支持Markdown格式）" />
          </el-form-item>
          
          <el-divider content-position="center">开票信息</el-divider>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="抬头">
                <el-input v-model="form.invoice_info" placeholder="请输入发票抬头" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="税号">
                <el-input v-model="form.tax_number" placeholder="请输入税号" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="开户行">
                <el-input v-model="form.bank_name" placeholder="请输入开户银行" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="账号">
                <el-input v-model="form.bank_account" placeholder="请输入银行账号" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="地址">
                <el-input v-model="form.invoice_address" placeholder="请输入开票地址" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="电话">
                <el-input v-model="form.invoice_phone" placeholder="请输入开票电话" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>
      
      <template #footer>
        <div class="drawer-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
        </div>
      </template>
    </el-drawer>

    <!-- 详情抽屉 -->
    <el-drawer
      v-model="detailVisible"
      :title="detailTitle"
      size="700px"
      :close-on-click-modal="false"
    >
      <div v-loading="detailLoading">
        <template v-if="detail">
          <el-divider content-position="center">基本信息</el-divider>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="客户名称">{{ detail.name }}</el-descriptions-item>
            <el-descriptions-item label="客户类型">
              <el-tag :type="getTypeTag(detail.type)" size="small">{{ getTypeLabel(detail.type) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="所属行业">{{ detail.industry || '-' }}</el-descriptions-item>
            <el-descriptions-item label="企业规模">
              <el-tag :type="getScaleTag(detail.scale)" size="small">{{ getScaleLabel(detail.scale) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="联系电话">{{ detail.phone || '-' }}</el-descriptions-item>
            <el-descriptions-item label="电子邮箱">{{ detail.email || '-' }}</el-descriptions-item>
            <el-descriptions-item label="公司地址" :span="2">{{ detail.address || '-' }}</el-descriptions-item>
            <el-descriptions-item label="潜力评分">
              <el-rate v-model="detail.potential_score" disabled />
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ detail.created_at }}</el-descriptions-item>
            <el-descriptions-item label="创建人">{{ detail.created_by }}</el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">{{ detail.notes || '-' }}</el-descriptions-item>
            <el-descriptions-item label="简介" :span="2">
              <div v-if="detail.description" v-html="renderMarkdown(detail.description)"></div>
              <span v-else>-</span>
            </el-descriptions-item>
          </el-descriptions>
          
          <el-divider content-position="center">开票信息</el-divider>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="抬头">{{ detail.invoice_info || '-' }}</el-descriptions-item>
            <el-descriptions-item label="税号">{{ detail.tax_number || '-' }}</el-descriptions-item>
            <el-descriptions-item label="开户行">{{ detail.bank_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="账号">{{ detail.bank_account || '-' }}</el-descriptions-item>
            <el-descriptions-item label="地址">{{ detail.invoice_address || '-' }}</el-descriptions-item>
            <el-descriptions-item label="电话">{{ detail.invoice_phone || '-' }}</el-descriptions-item>
          </el-descriptions>
          
          <el-divider content-position="center">联系人列表</el-divider>
          <el-table v-if="relatedContacts.length > 0" :data="relatedContacts" size="small" border>
            <el-table-column prop="name" label="姓名" min-width="120" />
            <el-table-column prop="position" label="职位" min-width="150" />
            <el-table-column prop="phone" label="电话" min-width="150" />
            <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
          </el-table>
          <el-empty v-else description="暂无联系人" :image-size="60" />
          
          <el-divider content-position="center">商机列表</el-divider>
          <el-table v-if="relatedOpportunities.length > 0" :data="relatedOpportunities" size="small" border>
            <el-table-column prop="opportunity_name" label="商机名称" min-width="200" />
            <el-table-column prop="stage" label="阶段" min-width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ row.stage }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="estimated_amount" label="金额" min-width="130">
              <template #default="{ row }">
                <span class="amount-text">¥{{ row.estimated_amount?.toLocaleString() }}</span>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="暂无商机" :image-size="60" />
          
          <el-divider content-position="center">跟踪记录</el-divider>
          <el-table v-if="relatedFollowups.length > 0" :data="relatedFollowups" size="small" border>
            <el-table-column prop="title" label="待办事项" min-width="200" />
            <el-table-column prop="type" label="类型" min-width="100" />
            <el-table-column prop="due_date" label="截止日期" min-width="120" />
          </el-table>
          <el-empty v-else description="暂无跟进记录" :image-size="60" />
        </template>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox, FormInstance, FormRules } from 'element-plus'
import { getCustomerList, getCustomerDetail, createCustomer, updateCustomer, deleteCustomer } from '@/api/customer'
import { getContactList } from '@/api/contact'
import { getOpportunityList } from '@/api/opportunity'
import dayjs from 'dayjs'

// 简单的Markdown渲染（处理换行和粗体）
function renderMarkdown(text: string): string {
  if (!text) return ''
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

const router = useRouter()
const route = useRoute()

// 行业选项
const industryOptions = [
  '能源电力', '金融银行', '政府机构', '制造业', '医疗卫生', 
  '教育培训', '交通运输', '房地产', '通信科技', '其他'
]

// 列表查询参数
const query = reactive({
  page: 1,
  pageSize: 20,
  keyword: '',
  type: '',
  industry: ''
})

// 表格数据
const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)
const selection = ref<any[]>([])
const selectedRows = ref<any[]>([])
const tableRef = ref()

// 弹窗
const dialogVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()
const editingId = ref<number | null>(null)
const searchInputRef = ref()
const form = reactive<any>({
  name: '',
  type: 'final_customer',
  industry: '',
  scale: 'medium',
  phone: '',
  email: '',
  address: '',
  potential_score: 3,
  invoice_info: '',
  tax_number: '',
  bank_account: '',
  bank_name: '',
  invoice_address: '',
  invoice_phone: '',
  notes: '',
  description: ''
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择客户类型', trigger: 'change' }],
  industry: [{ required: true, message: '请选择所属行业', trigger: 'change' }]
}

// 详情
const detailVisible = ref(false)
const detailLoading = ref(false)
const detail = ref<any>(null)
const detailTitle = ref('客户详情')
const relatedContacts = ref<any[]>([])
const relatedOpportunities = ref<any[]>([])
const relatedFollowups = ref<any[]>([])

// 获取列表数据
async function fetchData() {
  loading.value = true
  try {
    const data = await getCustomerList(query)
    tableData.value = data.items || []
    total.value = data.total || 0
  } catch (error) {
    console.error('获取客户列表失败', error)
  } finally {
    loading.value = false
  }
}

// 搜索
function handleSearch() {
  query.page = 1
  fetchData()
}

// 重置
function handleReset() {
  query.keyword = ''
  query.type = ''
  query.industry = ''
  query.page = 1
  fetchData()
}

// 新建
function handleAdd() {
  router.push('/customer/detail/new')
}

// 编辑
function handleEdit(row: any) {
  editingId.value = row.id
  Object.assign(form, {
    name: row.name,
    type: row.type,
    industry: row.industry,
    scale: row.scale,
    phone: row.phone,
    email: row.email,
    address: row.address,
    potential_score: row.potential_score,
    notes: row.notes,
    description: row.description,
    invoice_info: row.invoice_info,
    tax_number: row.tax_number,
    bank_account: row.bank_account,
    bank_name: row.bank_name,
    invoice_address: row.invoice_address,
    invoice_phone: row.invoice_phone
  })
  dialogVisible.value = true
}

// 查看详情
async function handleView(row: any) {
  detailTitle.value = `客户详情 - ${row.name}`
  detailVisible.value = true
  detailLoading.value = true
  try {
    detail.value = await getCustomerDetail(row.id)
    // 获取关联联系人
    const contactData = await getContactList({ org_id: row.id, page: 1, pageSize: 100 })
    relatedContacts.value = contactData.items || []
    // 获取关联商机
    const oppData = await getOpportunityList({ org_id: row.id, page: 1, pageSize: 100 })
    relatedOpportunities.value = oppData.items || []
    // 关联跟进记录（模拟数据，实际应从API获取）
    relatedFollowups.value = []
  } catch (error) {
    console.error('获取客户详情失败', error)
  } finally {
    detailLoading.value = false
  }
}

// 提交表单
async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitLoading.value = true
    try {
      if (editingId.value) {
        await updateCustomer(editingId.value, form)
        ElMessage.success('更新成功')
      } else {
        await createCustomer(form)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchData()
    } catch (error) {
      // 错误已由拦截器处理
    } finally {
      submitLoading.value = false
    }
  })
}

// 删除
async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm(`确定删除客户"${row.name}"吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteCustomer(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch {
    // 取消操作
  }
}

// 重置表单
function resetForm() {
  nextTick(() => {
    form.name = ''
    form.type = 'final_customer'
    form.industry = ''
    form.scale = 'medium'
    form.phone = ''
    form.email = ''
    form.address = ''
    form.potential_score = 3
    form.notes = ''
    form.description = ''
    form.invoice_info = ''
    form.tax_number = ''
    form.bank_name = ''
    form.bank_account = ''
    form.invoice_address = ''
    form.invoice_phone = ''
    formRef.value?.resetFields()
  })
}

// 弹窗关闭
function handleDialogClose() {
  resetForm()
}

// 工具方法
function getTypeTag(type: string) {
  const map: Record<string, string> = {
    'final_customer': '',
    'partner': 'success',
    'undecided': 'info'
  }
  return map[type] || 'info'
}

function getTypeLabel(type: string) {
  const map: Record<string, string> = {
    'final_customer': '最终客户',
    'partner': '合作伙伴',
    'undecided': '待定'
  }
  return map[type] || type
}

function getScaleTag(scale: string) {
  const map: Record<string, string> = {
    'small': 'success',
    'medium': '',
    'large': 'warning',
    'enterprise': 'danger'
  }
  return map[scale] || 'info'
}

function getScaleLabel(scale: string) {
  const map: Record<string, string> = {
    'small': '小型',
    'medium': '中型',
    'large': '大型',
    'enterprise': ' enterprise'
  }
  return map[scale] || scale
}

function isOverdue(date: string) {
  if (!date) return false
  return dayjs(date).isBefore(dayjs(), 'day')
}

function formatDate(date: string) {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD')
}

function handleSelectionChange(val: any[]) {
  selection.value = val
  selectedRows.value = val
}

function handleSizeChange(val: number) {
  query.pageSize = val
  fetchData()
}

async function handleBatchDelete() {
  if (!selectedRows.value.length) return
  try {
    await ElMessageBox.confirm(
      `确定删除选中的 ${selectedRows.value.length} 个客户吗？`,
      '批量删除',
      { type: 'warning' }
    )
    await Promise.all(selectedRows.value.map(row => deleteCustomer(row.id)))
    ElMessage.success('删除成功')
    selectedRows.value = []
    fetchData()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

function handleCommand(command: string, row: any) {
  switch (command) {
    case 'add-contact':
      router.push(`/contact?org_id=${row.id}`)
      break
    case 'add-opportunity':
      router.push(`/opportunity/list?org_id=${row.id}`)
      break
    case 'add-activity':
      router.push(`/activity?org_id=${row.id}`)
      break
    case 'transfer':
      handleTransfer(row)
      break
    case 'delete':
      handleDelete(row)
      break
  }
}

function handleTransfer(row: any) {
  ElMessage.info('转移客户功能开发中')
}

function handleViewContacts(row: any) {
  router.push(`/customer/contact?org_id=${row.id}`)
}

function handleViewOpportunities(row: any) {
  router.push(`/opportunity/list?org_id=${row.id}`)
}

function handleAddContact() {
  router.push(`/contact?org_id=${detail.value?.id}`)
}

function handleAddOpportunity() {
  router.push(`/opportunity/list?org_id=${detail.value?.id}`)
}

onMounted(async () => {
  window.addEventListener('keydown', handleGlobalKeydown)
  fetchData()
  // 检查URL查询参数，自动打开编辑
  const action = route.query.action
  const editId = route.query.id
  if (action === 'edit' && editId) {
    try {
      const data = await getCustomerDetail(Number(editId))
      handleEdit(data)
    } catch (error) {
      console.error('获取客户详情失败', error)
    }
  }
})

function handleGlobalKeydown(e: KeyboardEvent) {
  if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) {
    e.preventDefault()
    searchInputRef.value?.focus()
  }
}

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
})
</script>

<style scoped lang="scss">
.customer-page {
  .customer-name-cell {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .text-danger {
    color: #F56C6C;
  }
}

.drawer-form {
  padding: 0 20px;
  overflow-y: auto;
}

.drawer-footer {
  padding: 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.customer-form {
  .el-rate {
    margin-top: 6px;
  }
}

.detail-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #EBEEF5;
  
  h4 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    color: #303133;
  }
}

.search-shortcut-hint {
  font-size: 12px;
  color: #909399;
  margin-left: auto;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 12px;
  
  .selected-info {
    color: #606266;
    font-size: 14px;
  }
}
.detail-grid {
  display: flex;
  flex-wrap: wrap;
}
.detail-item {
  width: 50%;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  box-sizing: border-box;
  .label {
    color: #909399;
    font-weight: 500;
    display: inline-block;
    min-width: 80px;
  }
}
:deep(.el-table .el-table__header .el-table-column--操作 .cell),
:deep(.el-table .el-table__body .el-table-column--操作 .cell) {
  white-space: nowrap;
}
</style>
