<template>
  <div class="system-user-page">
    <div class="search-bar">
      <div class="search-form">
        <el-input v-model="query.keyword" placeholder="搜索用户名/姓名/邮箱..." clearable style="width: 260px" @keyup.enter="handleSearch">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
      </div>
      <div class="action-buttons">
        <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon>新增用户</el-button>
      </div>
    </div>

    <el-card shadow="never" class="table-card">
      <el-table v-loading="loading" :data="tableData" row-key="id" @selection-change="handleSelectionChange">
        <el-table-column type="selection" min-width="50" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="name" label="姓名" min-width="100" />
        <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
        <el-table-column prop="role" label="角色" min-width="120">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : ''">{{ row.role_name || (row.role === 'admin' ? '管理员' : '普通用户') }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ row.status === 1 ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_login" label="最后登录" min-width="160" />
        <el-table-column prop="created_at" label="创建时间" min-width="160" />
        <el-table-column label="操作" min-width="220">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEdit(row)"><el-icon><Edit /></el-icon>编辑</el-button>
            <el-button type="warning" link size="small" @click="handleChangePwd(row)"><el-icon><Key /></el-icon>修改密码</el-button>
            <el-popconfirm title="确定删除该用户？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button type="danger" link size="small"><el-icon><Delete /></el-icon>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination background layout="total, prev, pager, next, sizes, jumper"
          v-model:current-page="query.page" v-model:page-size="query.pageSize"
          :total="total" :page-sizes="[10, 20, 50, 100]"
          @current-change="fetchData" @size-change="handleSizeChange" />
      </div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '新增用户'" width="500px" @close="handleDialogClose">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="!isEdit" label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">保存 <span style="font-size:11px;opacity:0.7;margin-left:4px;">⌘↵</span></el-button>
      </template>
    </el-dialog>

    <!-- 修改密码弹窗 -->
    <el-dialog v-model="pwdDialogVisible" title="修改密码" width="420px" :close-on-click-modal="false">
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="80px">
        <el-form-item label="用户名">
          <el-input :model-value="editingUsername" disabled />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="pwdForm.newPassword" type="password" placeholder="请输入新密码" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="pwdForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitPwd" :loading="pwdLoading">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { Search, Plus, Edit, Delete, Key } from '@element-plus/icons-vue'
import { getUserList, createUser, updateUser, deleteUser, User } from '@/api/user'

const query = reactive({ keyword: '', page: 1, pageSize: 20 })
const loading = ref(false)
const tableData = ref<User[]>([])
const total = ref(0)
const selectedRows = ref<User[]>([])
const dialogVisible = ref(false)
const pwdDialogVisible = ref(false)
const pwdLoading = ref(false)
const pwdFormRef = ref<FormInstance>()
const editingId = ref<number | null>(null)
const editingUsername = ref('')
const pwdForm = reactive({ newPassword: '', confirmPassword: '' })
const validateConfirmPwd = (rule: any, value: string, callback: any) => {
  if (value !== pwdForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}
const pwdRules: FormRules = {
  newPassword: [{ required: true, message: '请输入新密码', trigger: 'blur' }, { min: 6, message: '密码至少6位', trigger: 'blur' }],
  confirmPassword: [{ required: true, message: '请再次输入新密码', trigger: 'blur' }, { validator: validateConfirmPwd, trigger: 'blur' }]
}
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  username: '', name: '', email: '', role: 'user' as string, status: 1, password: ''
})

const roleNameMap: Record<string, string> = { admin: '管理员', user: '普通用户' }

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码至少6位', trigger: 'blur' }]
}

function handleKeydown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
    e.preventDefault()
    if (dialogVisible.value) {
      handleSave()
    }
  }
}

async function fetchData() {
  loading.value = true
  try {
    const res: any = await getUserList(query)
    tableData.value = res.items || []
    total.value = res.total || 0
  } catch (e: any) {
    ElMessage.error(e?.message || '获取用户列表失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() { query.page = 1; fetchData() }
function handleSizeChange(val: number) { query.pageSize = val; fetchData() }
function handleSelectionChange(val: User[]) { selectedRows.value = val }

function handleAdd() {
  isEdit.value = false
  editingId.value = null
  Object.assign(form, { username: '', name: '', email: '', role: 'user', status: 1, password: '' })
  dialogVisible.value = true
}

function handleEdit(row: User) {
  isEdit.value = true
  editingId.value = row.id
  Object.assign(form, { username: row.username, name: row.name, email: row.email, role: row.role || 'user', status: row.status, password: '' })
  dialogVisible.value = true
}

function handleDialogClose() { formRef.value?.resetFields() }

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      if (isEdit.value && editingId.value) {
        const { password, ...updateData } = form
        await updateUser(editingId.value, updateData)
        ElMessage.success('更新成功')
      } else {
        await createUser(form as any)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchData()
    } catch (e: any) {
      ElMessage.error(e?.message || '操作失败')
    } finally {
      submitLoading.value = false
    }
  })
}

async function handleDelete(row: User) {
  try {
    await deleteUser(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e: any) {
    ElMessage.error(e?.message || '删除失败')
  }
}

async function handleChangePwd(row: User) {
  editingId.value = row.id
  editingUsername.value = row.username
  pwdForm.newPassword = ''
  pwdForm.confirmPassword = ''
  pwdDialogVisible.value = true
}

async function handleSubmitPwd() {
  if (!pwdFormRef.value) return
  await pwdFormRef.value.validate(async (valid) => {
    if (!valid) return
    pwdLoading.value = true
    try {
      await updateUser(editingId.value!, { password: pwdForm.newPassword })
      ElMessage.success('密码修改成功')
      pwdDialogVisible.value = false
    } catch (e: any) {
      ElMessage.error(e?.message || '修改失败')
    } finally {
      pwdLoading.value = false
    }
  })
}

onMounted(() => { window.addEventListener('keydown', handleKeydown); fetchData() })

onUnmounted(() => { window.removeEventListener('keydown', handleKeydown) })
</script>

<style scoped lang="scss">
.system-user-page {
  .pagination-container { display: flex; justify-content: flex-end; padding: 16px 0 0; }
}
.search-bar {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 16px;
  .search-form { display: flex; gap: 12px; align-items: center; }
  .action-buttons { display: flex; gap: 12px; }
}
:deep(.el-table .el-table__header .el-table-column--操作 .cell),
:deep(.el-table .el-table__body .el-table-column--操作 .cell) {
  white-space: nowrap;
}
</style>
