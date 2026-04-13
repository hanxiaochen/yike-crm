<template>
  <div class="system-role-page">
    <div class="search-bar">
      <div class="action-buttons">
        <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon>新增角色</el-button>
      </div>
    </div>

    <el-card shadow="never" class="table-card">
      <el-table v-loading="loading" :data="tableData" row-key="id">
        <el-table-column prop="name" label="角色名称" min-width="150" />
        <el-table-column prop="code" label="角色代码" min-width="120" />
        <el-table-column prop="description" label="描述" min-width="300" show-overflow-tooltip />
        <el-table-column prop="userCount" label="用户数" min-width="100" align="center" />
        <el-table-column prop="status" label="状态" min-width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ row.status === 1 ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="180">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handlePermission(row)"><el-icon><Setting /></el-icon>权限</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 权限配置弹窗 -->
    <el-dialog v-model="permDialogVisible" title="角色权限配置" width="650px" :close-on-click-modal="false">
      <div v-if="currentRole">
        <div class="perm-header">
          <span>角色：<strong>{{ currentRole.name }}</strong></span>
          <el-tag v-if="currentRole.is_system" type="warning" size="small">系统角色</el-tag>
        </div>
        <p class="perm-desc">{{ currentRole.description }}</p>
        
        <el-alert v-if="currentRole.is_system" type="warning" :closable="false" show-icon style="margin-bottom: 16px;">
          系统角色拥有全部权限，不可修改。
        </el-alert>

        <div v-else class="perm-tree-container">
          <el-tree
            ref="permTreeRef"
            :data="permissionTree"
            show-checkbox
            node-key="key"
            :props="{ children: 'children', label: 'label' }"
            default-expand-all
            :expand-on-click-node="false"
          >
            <template #default="{ data }">
              <span class="perm-node">
                <span class="perm-label">{{ data.label }}</span>
                <span v-if="data.actions" class="perm-actions">
                  <el-checkbox 
                    v-for="action in data.actions" 
                    :key="action.key"
                    :label="action.key"
                    :checked="hasPermission(data.module, action.key)"
                    @change="(val: boolean) => togglePermission(data.module, action.key, val)"
                    :disabled="currentRole.is_system"
                  >{{ action.label }}</el-checkbox>
                </span>
              </span>
            </template>
          </el-tree>
        </div>
      </div>
      <template #footer>
        <el-button @click="permDialogVisible = false">取消</el-button>
        <el-button v-if="!currentRole?.is_system" type="primary" @click="handleSavePermissions" :loading="permLoading">保存 <span style="font-size:11px;opacity:0.7;margin-left:4px;">⌘↵</span></el-button>
      </template>
    </el-dialog>

    <!-- 新增角色弹窗 -->
    <el-dialog v-model="addDialogVisible" title="新增角色" width="500px">
      <el-form ref="formRef" :model="form" label-width="80px" :rules="formRules">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色代码" prop="code">
          <el-input v-model="form.code" placeholder="请输入角色代码（英文）" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddSubmit" :loading="addLoading">保存 <span style="font-size:11px;opacity:0.7;margin-left:4px;">⌘↵</span></el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Setting } from '@element-plus/icons-vue'
import { getRoleList, updateRolePermissions, Role } from '@/api/role'

const loading = ref(false)
const permLoading = ref(false)
const addLoading = ref(false)
const tableData = ref<Role[]>([])
const permDialogVisible = ref(false)
const addDialogVisible = ref(false)
const currentRole = ref<Role | null>(null)
const permTreeRef = ref()
const formRef = ref()
const currentPermissions = ref<Record<string, string[]>>({})

const form = reactive({ name: '', code: '', description: '' })
const formRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色代码', trigger: 'blur' }]
}

// 权限模块定义
const permissionModules = [
  { module: 'customers', label: '客户管理', actions: [
    { key: 'view', label: '查看' },
    { key: 'create', label: '新建' },
    { key: 'edit', label: '编辑' },
    { key: 'delete', label: '删除' }
  ]},
  { module: 'contacts', label: '联系人管理', actions: [
    { key: 'view', label: '查看' },
    { key: 'create', label: '新建' },
    { key: 'edit', label: '编辑' },
    { key: 'delete', label: '删除' }
  ]},
  { module: 'contracts', label: '合同管理', actions: [
    { key: 'view', label: '查看' },
    { key: 'create', label: '新建' },
    { key: 'edit', label: '编辑' },
    { key: 'delete', label: '删除' }
  ]},
  { module: 'invoices', label: '发票管理', actions: [
    { key: 'view', label: '查看' },
    { key: 'create', label: '新建' },
    { key: 'edit', label: '编辑' },
    { key: 'delete', label: '删除' }
  ]},
  { module: 'opportunities', label: '商机管理', actions: [
    { key: 'view', label: '查看' },
    { key: 'create', label: '新建' },
    { key: 'edit', label: '编辑' },
    { key: 'delete', label: '删除' }
  ]},
  { module: 'activities', label: '活动管理', actions: [
    { key: 'view', label: '查看' },
    { key: 'create', label: '新建' },
    { key: 'edit', label: '编辑' },
    { key: 'delete', label: '删除' }
  ]},
  { module: 'followups', label: '跟进记录', actions: [
    { key: 'view', label: '查看' },
    { key: 'create', label: '新建' },
    { key: 'edit', label: '编辑' },
    { key: 'delete', label: '删除' }
  ]},
  { module: 'insights', label: '数据洞察', actions: [
    { key: 'view', label: '查看' },
    { key: 'edit', label: '编辑' }
  ]},
  { module: 'users', label: '用户管理', actions: [
    { key: 'view', label: '查看' },
    { key: 'create', label: '新建' },
    { key: 'edit', label: '编辑' },
    { key: 'delete', label: '删除' }
  ]},
  { module: 'roles', label: '角色管理', actions: [
    { key: 'view', label: '查看' },
    { key: 'create', label: '新建' },
    { key: 'edit', label: '编辑' },
    { key: 'delete', label: '删除' }
  ]}
]

// 构建权限树
const permissionTree = computed(() => {
  return permissionModules.map(mod => ({
    key: mod.module,
    module: mod.module,
    label: mod.label,
    actions: mod.actions,
    children: mod.actions.map(act => ({
      key: `${mod.module}:${act.key}`,
      module: mod.module,
      label: act.label,
      actions: null
    }))
  }))
})

function handleKeydown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
    e.preventDefault()
    if (permDialogVisible.value) {
      handleSavePermissions()
    } else if (addDialogVisible.value) {
      handleAddSubmit()
    }
  }
}

function hasPermission(module: string, action: string): boolean {
  const perms = currentPermissions.value[module] || []
  return perms.includes(action)
}

function togglePermission(module: string, action: string, checked: boolean) {
  if (!currentPermissions.value[module]) {
    currentPermissions.value[module] = []
  }
  const idx = currentPermissions.value[module].indexOf(action)
  if (checked && idx === -1) {
    currentPermissions.value[module].push(action)
  } else if (!checked && idx !== -1) {
    currentPermissions.value[module].splice(idx, 1)
  }
}

async function fetchData() {
  loading.value = true
  try {
    const res: any = await getRoleList()
    tableData.value = res.items || []
  } catch (e: any) {
    ElMessage.error(e?.message || '获取角色列表失败')
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  Object.assign(form, { name: '', code: '', description: '' })
  addDialogVisible.value = true
}

function handlePermission(row: Role) {
  currentRole.value = row
  // 初始化当前权限
  currentPermissions.value = {}
  if (row.permissions) {
    for (const [mod, perms] of Object.entries(row.permissions)) {
      currentPermissions.value[mod] = perms as string[]
    }
  }
  permDialogVisible.value = true
}

async function handleSavePermissions() {
  if (!currentRole.value) return
  permLoading.value = true
  try {
    await updateRolePermissions(currentRole.value.id, currentPermissions.value)
    ElMessage.success('权限保存成功')
    permDialogVisible.value = false
    fetchData()
  } catch (e: any) {
    ElMessage.error(e?.message || '权限保存失败')
  } finally {
    permLoading.value = false
  }
}

function handleAddSubmit() {
  ElMessage.info('新增角色功能开发中')
  addDialogVisible.value = false
}

onMounted(() => { window.addEventListener('keydown', handleKeydown); fetchData() })

onUnmounted(() => { window.removeEventListener('keydown', handleKeydown) })
</script>

<style scoped lang="scss">
.search-bar {
  display: flex; justify-content: flex-end; align-items: center;
  margin-bottom: 16px;
  .action-buttons { display: flex; gap: 12px; }
}
.perm-header {
  display: flex; align-items: center; gap: 12px;
  margin-bottom: 8px;
}
.perm-desc {
  color: #909399; font-size: 13px; margin: 0 0 16px 0;
}
.perm-tree-container {
  max-height: 400px; overflow-y: auto;
  border: 1px solid #ebeef5; border-radius: 4px; padding: 12px;
}
:deep(.el-tree-node__content) {
  height: auto; padding: 4px 0;
}
.perm-node {
  display: flex; align-items: center; flex-wrap: wrap; gap: 12px;
  .perm-label { font-weight: 500; min-width: 80px; }
  .perm-actions { display: flex; gap: 16px; flex-wrap: wrap; }
}
:deep(.el-table .el-table__header .el-table-column--操作 .cell),
:deep(.el-table .el-table__body .el-table-column--操作 .cell) {
  white-space: nowrap;
}
</style>
