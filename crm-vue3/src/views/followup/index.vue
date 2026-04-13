<template>
  <div class="followup-page">
    <el-row :gutter="16">
      <el-col :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-icon todo-icon"><el-icon><Bell /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.todo }}</div>
            <div class="stat-label">待办</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-icon overdue-icon"><el-icon><Clock /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.overdue }}</div>
            <div class="stat-label">已过期</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-icon done-icon"><el-icon><Check /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.done }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-icon total-icon"><el-icon><Calendar /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">总计</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <div class="action-bar">
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
          新建待办
        </el-button>
      </div>
    </div>

    <el-card shadow="never" class="table-card" style="margin-top: 16px;">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="待办" name="todo">
          <template #label><el-badge :value="stats.todo" :hidden="stats.todo === 0">待办</el-badge></template>
        </el-tab-pane>
        <el-tab-pane label="已过期" name="overdue">
          <template #label><el-badge :value="stats.overdue" :hidden="stats.overdue === 0" type="danger">已过期</el-badge></template>
        </el-tab-pane>
        <el-tab-pane label="已完成" name="done" />
      </el-tabs>

      <el-table v-loading="loading" :data="tableData" row-key="id" @selection-change="handleSelectionChange">
        <el-table-column type="selection" min-width="50" />
        <el-table-column prop="title" label="待办事项" min-width="250">
          <template #default="{ row }">
            <span :class="{ 'line-through': row.done }">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" min-width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="org_name" label="客户" min-width="150" />
        <el-table-column prop="due_date" label="截止日期" min-width="120">
          <template #default="{ row }">
            <span :class="{ 'text-danger': isOverdue(row.due_date) && !row.done }">
              {{ row.due_date }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" min-width="80">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">{{ getPriorityLabel(row.priority) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="180">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button type="primary" link size="small" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-popconfirm title="确定删除该待办？" @confirm="handleDelete(row)">
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
    </el-card>

    <!-- 详情抽屉 -->
    <el-drawer v-model="detailVisible" title="待办详情" size="500px">
      <div v-if="detail" class="followup-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="待办事项" :span="2">{{ detail.title }}</el-descriptions-item>
          <el-descriptions-item label="类型">
            <el-tag size="small">{{ detail.type }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityType(detail.priority)" size="small">{{ getPriorityLabel(detail.priority) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="客户">{{ detail.org_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="截止日期">
            <span :class="{ 'text-danger': isOverdue(detail.due_date) && !detail.done }">{{ detail.due_date }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="detail.done ? 'success' : ''" size="small">{{ detail.done ? '已完成' : '未完成' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建人">{{ detail.created_by || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const activeTab = ref('all')
const loading = ref(false)
const tableData = ref<any[]>([])
const stats = reactive({ todo: 0, overdue: 0, done: 0, total: 0 })
const selectedRows = ref<any[]>([])
const detailVisible = ref(false)
const detail = ref<any>(null)

// 模拟数据
const mockData = [
  { id: 1, title: '联系华能集团张总确认项目需求', type: '跟进', org_name: '华能集团', due_date: dayjs().format('YYYY-MM-DD'), priority: 'high', done: false, created_by: '韩晓晨' },
  { id: 2, title: '跟进国电集团合同签订', type: '签约', org_name: '国电集团', due_date: dayjs().subtract(1, 'day').format('YYYY-MM-DD'), priority: 'urgent', done: false, created_by: '韩晓晨' },
  { id: 3, title: '准备大唐发电技术方案', type: '跟进', org_name: '大唐发电', due_date: dayjs().add(1, 'day').format('YYYY-MM-DD'), priority: 'medium', done: false, created_by: '韩晓晨' },
  { id: 4, title: '发送报价文件给客户', type: '其他', org_name: '华能集团', due_date: dayjs().format('YYYY-MM-DD'), priority: 'low', done: true, created_by: '韩晓晨' },
]

function handleTabChange() {
  // 可以根据tab筛选数据
}

function handleSelectionChange(val: any[]) {
  selectedRows.value = val
}

function handleBatchDelete() {
  if (!selectedRows.value.length) return
  ElMessage.info('批量删除功能开发中')
}

function handleView(row: any) {
  detail.value = row
  detailVisible.value = true
}

function handleEdit(row: any) {
  ElMessage.info('编辑功能开发中')
}

async function handleCheck(row: any) {
  ElMessage.success(row.done ? '已标记为完成' : '已取消完成')
}

async function handleDelete(row: any) {
  try {
    tableData.value = tableData.value.filter(d => d.id !== row.id)
    updateStats()
    ElMessage.success('删除成功')
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

function isOverdue(date: string) {
  if (!date) return false
  return dayjs(date).isBefore(dayjs(), 'day')
}

function getPriorityType(p: string) {
  return { urgent: 'danger', high: 'warning', medium: '', low: 'info' }[p] || 'info'
}

function getPriorityLabel(p: string) {
  return { urgent: '紧急', high: '高', medium: '中', low: '低' }[p] || p
}

function updateStats() {
  stats.total = tableData.value.length
  stats.todo = tableData.value.filter(d => !d.done && !isOverdue(d.due_date)).length
  stats.overdue = tableData.value.filter(d => !d.done && isOverdue(d.due_date)).length
  stats.done = tableData.value.filter(d => d.done).length
}

onMounted(() => {
  tableData.value = mockData
  updateStats()
})
</script>

<style scoped lang="scss">
.followup-page {
  .stat-card {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
    
    .stat-icon {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      
      &.todo-icon { background: rgba(64,158,255,0.1); color: #409EFF; }
      &.overdue-icon { background: rgba(245,108,108,0.1); color: #F56C6C; }
      &.done-icon { background: rgba(103,194,58,0.1); color: #67C23A; }
      &.total-icon { background: rgba(144,147,153,0.1); color: #909399; }
    }
    
    .stat-info {
      .stat-value { font-size: 24px; font-weight: 700; color: #303133; }
      .stat-label { font-size: 13px; color: #909399; margin-top: 4px; }
    }
  }
  
  .line-through { text-decoration: line-through; color: #C0C4CC; }
  .text-danger { color: #F56C6C; font-weight: 500; }
}

.action-bar {
  margin-top: 16px;
  
  .action-buttons {
    display: flex;
    align-items: center;
    gap: 12px;
    
    .selected-info {
      color: #606266;
      font-size: 14px;
    }
  }
}
:deep(.el-table .el-table__header .el-table-column--操作 .cell),
:deep(.el-table .el-table__body .el-table-column--操作 .cell) {
  white-space: nowrap;
}
</style>
