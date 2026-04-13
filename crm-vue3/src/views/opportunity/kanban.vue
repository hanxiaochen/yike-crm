<template>
  <div class="opportunity-kanban">
    <!-- 工具栏 -->
    <div class="kanban-toolbar">
      <div class="toolbar-left">
        <h2 class="page-title">商机看板</h2>
        <span class="total-amount">总金额：¥{{ totalAmount }}</span>
      </div>
      <div class="toolbar-right">
        <el-radio-group v-model="viewMode" size="small">
          <el-radio-button value="kanban">看板视图</el-radio-button>
          <el-radio-button value="list">列表视图</el-radio-button>
        </el-radio-group>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新建商机
        </el-button>
      </div>
    </div>

    <!-- 看板列 -->
    <div class="kanban-board">
      <div 
        v-for="stage in stages" 
        :key="stage.key" 
        class="kanban-column"
      >
        <div class="column-header" :style="{ borderColor: stage.color }">
          <div class="column-title">
            <span class="stage-dot" :style="{ background: stage.color }"></span>
            <span>{{ stage.label }}</span>
            <el-badge :value="getStageItems(stage.key).length" class="stage-count" />
          </div>
          <div class="column-amount">
            ¥{{ getStageAmount(stage.key) }}
          </div>
        </div>
        
        <div 
          class="column-body"
          @dragover.prevent
          @drop="handleDrop($event, stage.key)"
        >
          <div 
            v-for="item in getStageItems(stage.key)" 
            :key="item.id" 
            class="kanban-card"
            draggable="true"
            @dragstart="handleDragStart($event, item)"
            @click="handleView(item)"
          >
            <div class="card-header">
              <el-tag size="small" :type="getPriorityType(item.priority)" effect="plain">
                {{ getPriorityLabel(item.priority) }}
              </el-tag>
              <span class="card-probability">{{ item.probability }}%</span>
            </div>
            <div class="card-title">{{ item.opportunity_name }}</div>
            <div class="card-org">
              <el-icon><OfficeBuilding /></el-icon>
              {{ item.org_name }}
            </div>
            <div class="card-footer">
              <span class="card-amount">¥{{ formatAmount(item.estimated_amount) }}</span>
              <span class="card-date">{{ formatDate(item.estimated_close_date) }}</span>
            </div>
          </div>
          
          <div v-if="getStageItems(stage.key).length === 0" class="empty-column">
            <el-icon><Folder /></el-icon>
            <span>暂无商机</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 详情抽屉 -->
    <el-drawer
      v-model="detailVisible"
      title="商机详情"
      size="600px"
      :close-on-click-modal="false"
    >
      <div v-loading="detailLoading" v-if="detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="商机名称" :span="2">
            {{ detail.opportunity_name }}
          </el-descriptions-item>
          <el-descriptions-item label="所属客户">
            <el-link type="primary">{{ detail.org_name }}</el-link>
          </el-descriptions-item>
          <el-descriptions-item label="采购阶段">
            <el-tag :style="getStageStyle(detail.stage)" effect="plain">
              {{ getStageLabel(detail.stage) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="商机金额">
            <span class="amount-text">¥{{ detail.estimated_amount?.toLocaleString() }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="成交概率">
            <el-progress :percentage="detail.probability" :color="getStageColor(detail.stage)" />
          </el-descriptions-item>
          <el-descriptions-item label="预测类别">
            {{ getForecastLabel(detail.forecast_category) || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="销售预期">
            <span class="sales-expectation">{{ calcSalesExpectation(detail.estimated_amount, detail.forecast_category) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="预计成交日期">
            {{ formatDate(detail.estimated_close_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityType(detail.priority)">
              {{ getPriorityLabel(detail.priority) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="负责人">{{ detail.assigned_to }}</el-descriptions-item>
          <el-descriptions-item label="商机来源">{{ detail.source || '-' }}</el-descriptions-item>
          <el-descriptions-item label="客户需求" :span="2">
            {{ detail.requirements || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="竞争对手">{{ detail.competitors || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ detail.created_at }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="detail-section">
          <h4>跟进记录</h4>
          <el-button type="primary" link size="small" @click="handleAddActivity">
            <el-icon><Plus /></el-icon>
            添加记录
          </el-button>
        </div>
        
        <el-timeline v-if="activities.length > 0">
          <el-timeline-item 
            v-for="act in activities" 
            :key="act.id"
            :timestamp="act.activity_date"
            placement="top"
          >
            <el-card shadow="never">
              <div class="activity-header">
                <el-tag size="small">{{ act.activity_type }}</el-tag>
                <span>{{ act.summary }}</span>
              </div>
              <div class="activity-detail" v-if="act.details">{{ act.details }}</div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getOpportunityList, updateOpportunityStage, getOpportunityDetail, getOpportunityActivities } from '@/api/opportunity'
import dayjs from 'dayjs'

// 阶段配置
const stages = [
  { key: 'business_driven', label: '① 业务驱动（10%）', color: '#909399' },
  { key: 'needs_defined', label: '② 确定需求（30%）', color: '#409eff' },
  { key: 'evaluation', label: '③ 评估方案（50%）', color: '#e6a23c' },
  { key: 'procurement', label: '④ 制定规则（70%）', color: '#f56c6c' },
  { key: 'contract_signed', label: '⑤ 签订合同（90%）', color: '#7c3aed' },
  { key: 'payment_implementation', label: '⑥ 付款实施（100%）', color: '#10b981' },
  { key: 'closed_won', label: '赢单', color: '#67c23a' },
  { key: 'closed_lost', label: '输单', color: '#909399' }
]

const viewMode = ref('kanban')
const tableData = ref<any[]>([])
const detailVisible = ref(false)
const detailLoading = ref(false)
const detail = ref<any>(null)
const activities = ref<any[]>([])

// 计算总金额
const totalAmount = computed(() => {
  const activeDeals = tableData.value.filter(d => d.stage !== 'closed_won' && d.stage !== 'closed_lost')
  return (activeDeals.reduce((sum, d) => sum + (d.estimated_amount || 0), 0) / 10000).toFixed(1) + '万'
})

// 获取阶段数据
function getStageItems(stage: string) {
  return tableData.value.filter(d => d.stage === stage)
}

function getStageAmount(stage: string) {
  const amount = getStageItems(stage).reduce((sum, d) => sum + (d.estimated_amount || 0), 0)
  return formatAmount(amount)
}

function formatAmount(amount: number) {
  if (!amount) return '0'
  if (amount >= 10000) return (amount / 10000).toFixed(1) + '万'
  return amount.toLocaleString()
}

function formatDate(date: string) {
  if (!date) return '-'
  return dayjs(date).format('MM-DD')
}

function getPriorityType(priority: string) {
  const map: Record<string, string> = {
    'urgent': 'danger',
    'high': 'warning',
    'medium': '',
    'low': 'info'
  }
  return map[priority] || 'info'
}

function getPriorityLabel(priority: string) {
  const map: Record<string, string> = {
    'urgent': '紧急',
    'high': '高',
    'medium': '中',
    'low': '低'
  }
  return map[priority] || priority
}

function getStageTag(stage: string) {
  const map: Record<string, string> = {
    'business_driven': 'info',
    'needs_defined': 'primary',
    'evaluation': 'warning',
    'procurement': 'danger',
    'contract_signed': 'success',
    'payment_implementation': 'success',
    'closed_won': 'success',
    'closed_lost': 'info'
  }
  return map[stage] || 'info'
}

function getStageStyle(stage: string) {
  const styleMap: Record<string, string> = {
    'business_driven': 'background:#f4f4f5;color:#909399;border-color:#d3d4d6;',
    'needs_defined': 'background:#ecf5ff;color:#409eff;border-color:#b3d8ff;',
    'evaluation': 'background:#fdf6ec;color:#e6a23c;border-color:#faecd8;',
    'procurement': 'background:#fef0f0;color:#f56c6c;border-color:#fde2e2;',
    'contract_signed': 'background:#f0f9ff;color:#7c3aed;border-color:#ddebf7;',
    'payment_implementation': 'background:#e8f8f5;color:#10b981;border-color:#d1fae5;',
    'closed_won': 'background:#f0f9eb;color:#67c23a;border-color:#c2e7b0;',
    'closed_lost': 'background:#f4f4f5;color:#909399;border-color:#d9d9d9;'
  }
  return styleMap[stage] || ''
}

function getStageLabel(stage: string) {
  const stageInfo = stages.find(s => s.key === stage)
  return stageInfo?.label || stage
}

function getStageColor(stage: string) {
  const stageInfo = stages.find(s => s.key === stage)
  return stageInfo?.color || '#409EFF'
}

function getForecastLabel(category: string) {
  const map: Record<string, string> = {
    opportunity: '机会',
    possible_minus: '可能-',
    possible_plus: '可能+',
    advantage: '优势',
    ensure: '确保'
  }
  return map[category] || ''
}

function calcSalesExpectation(amount: number, category: string) {
  const aMap: Record<string, number> = {
    opportunity: 0,
    possible_minus: 0.2,
    possible_plus: 0.6,
    advantage: 0.9,
    ensure: 1
  }
  const a = aMap[category] ?? 0
  const val = amount * a
  return '¥' + val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// 拖拽
let dragItem: any = null

function handleDragStart(event: DragEvent, item: any) {
  dragItem = item
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
  }
}

async function handleDrop(event: DragEvent, newStage: string) {
  event.preventDefault()
  if (!dragItem || dragItem.stage === newStage) return
  
  try {
    await updateOpportunityStage(dragItem.id, newStage)
    
    // 更新本地数据
    const item = tableData.value.find(d => d.id === dragItem.id)
    if (item) {
      item.stage = newStage
    }
    
    ElMessage.success('阶段更新成功')
  } catch (error) {
    console.error('更新阶段失败', error)
  }
  
  dragItem = null
}

// 查看详情
async function handleView(item: any) {
  detailVisible.value = true
  detailLoading.value = true
  try {
    detail.value = await getOpportunityDetail(item.id)
    activities.value = await getOpportunityActivities(item.id)
  } catch (error) {
    console.error('获取商机详情失败', error)
  } finally {
    detailLoading.value = false
  }
}

function handleAdd() {
  // 跳转新建页面
}

function handleAddActivity() {
  // 添加跟进记录
}

// 获取列表数据
async function fetchData() {
  try {
    const data = await getOpportunityList({ page: 1, pageSize: 1000 })
    tableData.value = data.items || []
  } catch (error) {
    console.error('获取商机列表失败', error)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
.opportunity-kanban {
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  background: #F5F7FA;
  padding: 16px;
  
  .kanban-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    .toolbar-left {
      display: flex;
      align-items: center;
      gap: 16px;
      
      .page-title {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
        color: #303133;
      }
      
      .total-amount {
        font-size: 14px;
        color: #E6A23C;
        font-weight: 500;
      }
    }
    
    .toolbar-right {
      display: flex;
      gap: 12px;
    }
  }
  
  .kanban-board {
    flex: 1;
    display: flex;
    gap: 12px;
    overflow-x: auto;
    padding-bottom: 16px;
    
    .kanban-column {
      min-width: 280px;
      max-width: 280px;
      background: #F5F7FA;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      
      .column-header {
        padding: 12px 16px;
        background: #fff;
        border-radius: 8px 8px 0 0;
        border-left: 3px solid;
        
        .column-title {
          display: flex;
          align-items: center;
          gap: 8px;
          font-weight: 600;
          color: #303133;
          
          .stage-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
          }
          
          .stage-count {
            margin-left: 4px;
          }
        }
        
        .column-amount {
          margin-top: 4px;
          font-size: 13px;
          color: #909399;
        }
      }
      
      .column-body {
        flex: 1;
        padding: 12px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 10px;
        
        .kanban-card {
          background: #fff;
          border-radius: 8px;
          padding: 12px;
          cursor: pointer;
          transition: all 0.2s;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          
          &:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transform: translateY(-2px);
          }
          
          .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            
            .card-probability {
              font-size: 12px;
              color: #909399;
            }
          }
          
          .card-title {
            font-size: 14px;
            font-weight: 500;
            color: #303133;
            margin-bottom: 6px;
            line-height: 1.4;
          }
          
          .card-org {
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 12px;
            color: #909399;
            margin-bottom: 10px;
          }
          
          .card-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            
            .card-amount {
              color: #E6A23C;
              font-weight: 600;
            }
            
            .card-date {
              color: #C0C4CC;
            }
          }
        }
        
        .empty-column {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          color: #C0C4CC;
          font-size: 13px;
          gap: 8px;
          min-height: 100px;
        }
      }
    }
  }
}

.detail-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 24px 0 16px;
  padding-top: 16px;
  border-top: 1px solid #EBEEF5;
  
  h4 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    color: #303133;
  }
}

.activity-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.activity-detail {
  margin-top: 8px;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

.amount-text {
  color: #E6A23C;
  font-weight: 600;
  font-size: 16px;
}

.sales-expectation {
  color: #67C23A;
  font-weight: 700;
  font-size: 15px;
}
</style>
