<template>
  <div class="contact-page">
    <template v-if="!detailMode">
      <div class="search-bar">
        <div class="search-form">
          <el-input
            ref="searchInputRef"
            v-model="query.keyword"
            placeholder="搜索姓名/电话/邮箱..."
            clearable
            style="width: 260px"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select v-model="query.org_id" placeholder="客户" clearable filterable style="width: 200px" @change="handleSearch">
            <el-option v-for="org in orgOptions" :key="org.id" :label="org.name" :value="org.id" />
          </el-select>
        </div>
        <span class="search-shortcut-hint">按 / 聚焦搜索</span>
        <div class="action-buttons">
          <span v-if="selectedRows.length > 0" class="selected-info">已选择 {{ selectedRows.length }} 项</span>
          <el-button v-if="selectedRows.length > 0" type="danger" @click="handleBatchDelete">
            <el-icon><Delete /></el-icon>批量删除
          </el-button>
          <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon>新建联系人</el-button>
        </div>
      </div>

      <el-card shadow="never" class="table-card">
        <el-table v-loading="loading" :data="tableData" row-key="id" @selection-change="handleSelectionChange" table-layout="auto">
          <el-table-column type="selection" min-width="50" />
          <el-table-column prop="name" label="姓名" min-width="120">
            <template #default="{ row }">
              <el-link type="primary" @click="handleView(row)">{{ row.name }}</el-link>
              <el-tag v-if="row.is_primary" size="small" type="success" style="margin-left: 4px;">主</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="department" label="部门" min-width="100" />
          <el-table-column prop="position" label="职位" min-width="100" />
          <el-table-column prop="org_name" label="客户" min-width="140">
            <template #default="{ row }">
              <el-link v-if="row.organization_id" type="primary" @click="router.push(`/customer/detail/${row.organization_id}`)">{{ row.org_name }}</el-link>
              <span v-else>否</span>
            </template>
          </el-table-column>
          <el-table-column prop="phone" label="电话" min-width="130">
            <template #default="{ row }">
              <a v-if="row.phone" :href="`tel:${row.phone}`" class="phone-link"><el-icon><Phone /></el-icon>{{ row.phone }}</a>
              <span v-else>否</span>
            </template>
          </el-table-column>
          <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip>
            <template #default="{ row }">
              <a v-if="row.email" :href="`mailto:${row.email}`" class="email-link">{{ row.email }}</a>
              <span v-else>否</span>
            </template>
          </el-table-column>
          <el-table-column prop="is_alumni" label="校友" min-width="70">
            <template #default="{ row }">
              <el-tag v-if="row.is_alumni" size="small" type="warning">是</el-tag>
              <span v-else>否</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="150">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="handleView(row)"><el-icon><View /></el-icon>查看</el-button>
              <el-button type="primary" link size="small" @click="handleEdit(row)"><el-icon><Edit /></el-icon>编辑</el-button>
              <el-popconfirm title="确定删除该联系人？" @confirm="handleDelete(row)">
                <template #reference>
                  <el-button type="danger" link size="small"><el-icon><Delete /></el-icon>删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-container">
          <el-pagination background layout="total, prev, pager, next, sizes, jumper" v-model:current-page="query.page" v-model:page-size="query.pageSize" :total="total" :page-sizes="[10, 20, 50, 100]" @current-change="fetchData" @size-change="handleSizeChange" />
        </div>
      </el-card>
    </template>

    <template v-if="detailMode">
      <div class="detail-header">
        <el-page-header :content="!editingId ? '新建联系人' : isEdit ? '编辑联系人' : '联系人详情'" @back="handleBack">
          <template #extra>
            <template v-if="!isEdit"><el-button type="primary" @click="handleEdit(detail!)">编辑</el-button></template>
            <template v-else><el-button @click="handleCancel">取消</el-button><el-button type="primary" @click="handleSave" :loading="submitLoading">保存 <span style="font-size:11px;opacity:0.7;margin-left:4px;">⌘↵</span></el-button><span class="shortcut-hint">ESC 返回</span></template>
          </template>
        </el-page-header>
      </div>

      <!-- 查看模式 -->
      <el-card shadow="never" style="margin-top: 20px;" v-if="!isEdit && detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="姓名">{{ detail.name }}</el-descriptions-item>
          <el-descriptions-item label="客户">
            <el-link v-if="detail.organization_id" type="primary" @click="router.push(`/customer/detail/${detail.organization_id}`)">{{ detail.org_name }}</el-link>
            <span v-else>否</span>
          </el-descriptions-item>
          <el-descriptions-item label="部门">{{ detail.department || '-' }}</el-descriptions-item>
          <el-descriptions-item label="职位">{{ detail.position || '-' }}</el-descriptions-item>
          <el-descriptions-item label="职责" :span="2">{{ detail.responsibility || '-' }}</el-descriptions-item>
          <el-descriptions-item label="电话">{{ detail.phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ detail.email || '-' }}</el-descriptions-item>
          <el-descriptions-item label="主联系人"><el-tag v-if="detail.is_primary" type="success">是</el-tag><span v-else>否</span></el-descriptions-item>
          <el-descriptions-item label="是否校友"><el-tag v-if="detail.is_alumni" type="warning">是</el-tag><span v-else>否</span></el-descriptions-item>
          <el-descriptions-item label="专业" :span="2">{{ detail.is_alumni ? (detail.major || '-') : '-' }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ detail.notes || '-' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 跟踪记录 -->
      <el-card shadow="never" style="margin-top: 20px;" v-if="!isEdit && detail">
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>跟踪记录</span>
            <el-button type="primary" size="small" @click="handleSaveFollowup" :loading="followupLoading">保存跟踪记录</el-button>
          </div>
        </template>
        <el-input v-model="followupText" type="textarea" :rows="4" placeholder="请输入跟踪记录内容（支持Markdown格式）" style="margin-bottom: 12px;" />
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

      <!-- 编辑模式 -->
      <el-card shadow="never" style="margin-top: 20px;" v-if="isEdit">
        <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="姓名" prop="name"><el-input v-model="form.name" placeholder="请输入姓名" /></el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="客户" prop="org_id">
                <el-select v-model="form.org_id" placeholder="选择客户" filterable style="width: 100%">
                  <el-option v-for="org in orgOptions" :key="org.id" :label="org.name" :value="org.id" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="部门"><el-input v-model="form.department" placeholder="请输入部门" /></el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="职位"><el-input v-model="form.position" placeholder="请输入职位" /></el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="职责"><el-input v-model="form.responsibility" placeholder="请输入职责" /></el-form-item>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="电话"><el-input v-model="form.phone" placeholder="请输入电话" /></el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="邮箱"><el-input v-model="form.email" placeholder="请输入邮箱" /></el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="主联系人"><el-switch v-model="form.is_primary" :active-value="1" :inactive-value="0" /></el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="是否校友"><el-switch v-model="form.is_alumni" :active-value="1" :inactive-value="0" /></el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16" v-if="form.is_alumni === 1">
            <el-col :span="12">
              <el-form-item label="专业"><el-input v-model="form.major" placeholder="请输入专业" /></el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="备注"><el-input v-model="form.notes" type="textarea" :rows="2" placeholder="请输入备注" /></el-form-item>
        </el-form>
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { getContactList, createContact, updateContact, deleteContact, getContactDetail } from '@/api/contact'
import { getCustomerList } from '@/api/customer'
import { request } from '@/api/request'
import { useUserStore } from '@/store/user'
import { UserFilled, Phone, Search, Plus, View, Edit, Delete } from '@element-plus/icons-vue'

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()

const detailMode = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)

const query = reactive({ page: 1, pageSize: 20, keyword: '', org_id: '' as any })
const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)
const selectedRows = ref<any[]>([])
const orgOptions = ref<any[]>([])
const dialogVisible = ref(false)
const formRef = ref<FormInstance>()
const searchInputRef = ref()
const editingId = ref<number | null>(null)
const detail = ref<any>(null)
const followupText = ref('')
const followupLoading = ref(false)
const followupRecords = ref<any[]>([])

const form = reactive<any>({
  name: '', org_id: '' as any, department: '', position: '', responsibility: '',
  phone: '', email: '', is_primary: 0, is_alumni: 0, major: '', notes: ''
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  org_id: [{ required: true, message: '请选择客户', trigger: 'change' }]
}

// 快捷键：Command/Ctrl + Enter 保存，ESC 返回
function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    e.preventDefault()
    if (detailMode.value) {
      handleBack()
    }
  } else if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
    e.preventDefault()
    if (dialogVisible.value) {
      handleSave()
    }
  } else if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) {
    e.preventDefault()
    searchInputRef.value?.focus()
  }
}

async function fetchData() {
  loading.value = true
  try {
    const data = await getContactList(query)
    tableData.value = data.items || []
    total.value = data.total || 0
  } catch (error) {
    console.error('获取联系人列表失败', error)
  } finally {
    loading.value = false
  }
}

async function fetchOrgOptions() {
  try {
    const res = await getCustomerList({ page: 1, pageSize: 1000 })
    orgOptions.value = res.items || []
  } catch (error) {
    console.error('获取客户列表失败', error)
  }
}

function handleSelectionChange(val: any[]) { selectedRows.value = val }

async function handleBatchDelete() {
  if (!selectedRows.value.length) return
  try {
    await Promise.all(selectedRows.value.map(row => deleteContact(row.id)))
    ElMessage.success('删除成功')
    selectedRows.value = []
    fetchData()
  } catch (e) { console.error(e) }
}

function handleSearch() { query.page = 1; fetchData() }
function handleSizeChange(val: number) { query.pageSize = val; fetchData() }

function handleAdd() {
  editingId.value = null
  Object.assign(form, { name: '', org_id: '' as any, department: '', position: '', responsibility: '', phone: '', email: '', is_primary: 0, is_alumni: 0, major: '', notes: '' })
  detailMode.value = true
  isEdit.value = true
}

function handleBack() {
  detailMode.value = false
  isEdit.value = false
  detail.value = null
  fetchData()
}

async function handleView(row: any) {
  try {
    detail.value = await getContactDetail(row.id)
    detailMode.value = true
    isEdit.value = false
    await fetchFollowupRecords()
  } catch (error) {
    ElMessage.error('获取联系人详情失败')
  }
}

function handleEdit(row: any) {
  editingId.value = row.id
  detail.value = row
  detailMode.value = true
  Object.assign(form, {
    name: row.name, org_id: row.organization_id || row.org_id, department: row.department || '',
    position: row.position || '', responsibility: row.responsibility || '',
    phone: row.phone || '', email: row.email || '',
    is_primary: row.is_primary || 0, is_alumni: row.is_alumni || 0, major: row.major || '',
    notes: row.notes || ''
  })
  isEdit.value = true
}

function handleCancel() {
  if (editingId.value) {
    isEdit.value = false
  } else {
    handleBack()
  }
}

async function handleSave() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      if (editingId.value) {
        await updateContact(editingId.value, form)
        ElMessage.success('更新成功')
        const updated = await getContactDetail(editingId.value)
        detail.value = updated
        isEdit.value = false
      } else {
        await createContact(form)
        ElMessage.success('创建成功')
        handleBack()
        return
      }
    } catch (error) {
      ElMessage.error('保存失败')
    } finally {
      submitLoading.value = false
    }
  })
}

async function handleDelete(row: any) {
  try {
    await deleteContact(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

async function handleSaveFollowup() {
  if (!followupText.value.trim()) {
    ElMessage.warning('请输入跟踪记录内容')
    return
  }
  followupLoading.value = true
  try {
    await request.post('/activities', {
      contact_id: detail.value.id,
      activity_type: 'other',
      activity_date: new Date().toISOString().slice(0, 19).replace('T', ' '),
      title: '联系人跟踪记录',
      description: followupText.value,
      recorded_by: userStore.userInfo?.name || '未知'
    })
    ElMessage.success('跟踪记录已保存')
    const now = new Date().toISOString().slice(0, 19).replace('T', ' ')
    followupRecords.value.unshift({
      id: Date.now(), title: '联系人跟踪记录',
      description: followupText.value,
      recorded_by: userStore.userInfo?.name || '未知',
      activity_date: now, created_at: now
    })
    followupText.value = ''
  } catch (error) {
    console.error('保存跟踪记录失败', error)
  } finally {
    followupLoading.value = false
  }
}

async function fetchFollowupRecords() {
  if (!detail.value?.id) return
  try {
    const data = await request.get('/activities', { contact_id: detail.value.id, page: 1, pageSize: 50 })
    followupRecords.value = (data.items || []).filter((r: any) => r.title?.includes('跟踪记录') && r.contact_id === detail.value.id)
  } catch (error) {
    console.error('获取跟踪记录失败', error)
  }
}

function renderMarkdown(text: string): string {
  if (!text) return ''
  return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>').replace(/\n/g, '<br>')
}

onMounted(async () => {
  window.addEventListener('keydown', handleKeydown)
  const contactId = route.query.id
  const action = route.query.action
  await fetchOrgOptions()
  if (contactId) {
    try {
      detail.value = await getContactDetail(Number(contactId))
      detailMode.value = true
      isEdit.value = action === 'edit'
      await fetchFollowupRecords()
    } catch (error) {
      console.error('获取联系人详情失败', error)
    }
  } else {
    fetchData()
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped lang="scss">
.contact-page {
  .detail-header { margin-bottom: 20px; }
  .shortcut-hint { font-size: 12px; color: #909399; margin-left: 12px; }
  .search-shortcut-hint { font-size: 12px; color: #909399; margin-left: auto; }
  .contact-name-cell { display: flex; align-items: center; gap: 8px; }
  .contact-info { display: flex; flex-direction: column; }
  .phone-link, .email-link { color: #409EFF; text-decoration: none; display: inline-flex; align-items: center; gap: 4px; }
  .pagination-container { display: flex; justify-content: flex-end; padding: 16px 0 0; }
  .action-buttons { display: flex; align-items: center; gap: 12px; .selected-info { color: #606266; font-size: 14px; } }
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
