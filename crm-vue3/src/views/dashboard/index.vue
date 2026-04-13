<template>
  <div class="dashboard-page">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-text">
        <h2>{{ greeting }}，{{ userName }} 👋</h2>
        <p class="sub-text">{{ currentDate }} · 继续努力！</p>
      </div>
      <div class="quick-actions">
        <el-button type="primary" @click="$router.push('/customer')">
          <el-icon><Plus /></el-icon>新建客户
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stat-card-grid">
      <div class="stat-card" v-for="stat in statCards" :key="stat.key" :style="{ '--accent-color': stat.color }">
        <div class="stat-icon" :style="{ background: stat.bgColor }">
          <el-icon :size="28" :color="stat.color"><component :is="stat.icon" /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
        <div class="stat-sub" v-if="stat.sub">{{ stat.sub }}</div>
      </div>
    </div>

    <!-- 第二行：图表 -->
    <div class="chart-grid">
      <el-card shadow="never" class="chart-card full-width">
        <template #header>
          <div class="card-header">
            <span>销售漏斗</span>
            <el-radio-group v-model="funnelPeriod" size="small">
              <el-radio-button value="week">本周</el-radio-button>
              <el-radio-button value="month">本月</el-radio-button>
              <el-radio-button value="quarter">本季</el-radio-button>
            </el-radio-group>
          </div>
        </template>
        <div ref="funnelChartRef" class="chart-container funnel-chart"></div>
      </el-card>
    </div>

    <!-- 第三行：左侧列表 + 右侧待办 -->
    <div class="main-grid">
      <!-- 左侧：今日待办 + 最近活动 -->
      <div class="left-column">
        <el-card shadow="never" class="list-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><Bell /></el-icon>今日待办</span>
              <el-badge :value="todayFollowups.length" :hidden="todayFollowups.length === 0">
                <el-button link type="primary" size="small" @click="$router.push('/followup')">查看全部</el-button>
              </el-badge>
            </div>
          </template>
          <div class="todo-list" v-if="todayFollowups.length > 0">
            <div v-for="item in todayFollowups" :key="item.id" class="todo-item">
              <el-checkbox :model-value="item.done" @change="toggleFollowup(item)" />
              <div class="todo-content">
                <div class="todo-title">{{ item.title }}</div>
                <div class="todo-org">{{ item.org_name }}</div>
              </div>
              <el-tag size="small" :type="getFollowupType(item.type)">{{ item.type }}</el-tag>
            </div>
          </div>
          <el-empty v-else description="今日无待办" :image-size="60" />
        </el-card>

        <el-card shadow="never" class="list-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><Clock /></el-icon>最近活动</span>
              <el-button link type="primary" size="small" @click="$router.push('/activity')">查看全部</el-button>
            </div>
          </template>
          <el-timeline v-if="recentActivities.length > 0" size="small">
            <el-timeline-item v-for="activity in recentActivities" :key="activity.id" :type="getActivityType(activity.type)" :timestamp="formatTime(activity.activity_date)" placement="top">
              <div class="activity-item">
                <div class="activity-title">{{ activity.title || activity.type }}</div>
                <div class="activity-desc" v-if="activity.description">{{ activity.description }}</div>
                <div class="activity-meta">
                  <span>{{ activity.org_name }}</span>
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无活动记录" :image-size="60" />
        </el-card>
      </div>

      <!-- 右侧：客户总览 + 商机动态 -->
      <div class="right-column">
        <el-card shadow="never" class="list-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><OfficeBuilding /></el-icon>客户总览</span>
              <el-button link type="primary" size="small" @click="$router.push('/customer')">全部客户</el-button>
            </div>
          </template>
          <div class="customer-summary">
            <div class="summary-item" v-for="item in customerSummary" :key="item.label">
              <span class="summary-value">{{ item.value }}</span>
              <span class="summary-label">{{ item.label }}</span>
            </div>
          </div>
          <div class="customer-list" v-if="recentCustomers.length > 0">
            <div v-for="customer in recentCustomers" :key="customer.id" class="customer-item">
              <div class="customer-info">
                <div class="customer-name">{{ customer.name }}</div>
                <el-tag size="small" :type="getCustomerType(customer.type)">{{ getCustomerTypeLabel(customer.type) }}</el-tag>
              </div>
              <div class="customer-meta">{{ customer.industry || '未分类' }}</div>
            </div>
          </div>
          <el-empty v-else description="暂无客户" :image-size="60" />
        </el-card>

        <el-card shadow="never" class="list-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><TrendCharts /></el-icon>商机动态</span>
              <el-button link type="primary" size="small" @click="$router.push('/opportunity')">查看全部</el-button>
            </div>
          </template>
          <div class="opportunity-stats" v-if="opportunityStats">
            <div class="opp-stat">
              <span class="opp-value">{{ opportunityStats.total }}</span>
              <span class="opp-label">进行中</span>
            </div>
            <div class="opp-stat">
              <span class="opp-value text-success">{{ opportunityStats.won }}</span>
              <span class="opp-label">赢单</span>
            </div>
            <div class="opp-stat">
              <span class="opp-value text-danger">{{ opportunityStats.lost }}</span>
              <span class="opp-label">输单</span>
            </div>
          </div>
          <div class="opportunity-list" v-if="recentOpportunities.length > 0">
            <div v-for="opp in recentOpportunities" :key="opp.id" class="opp-item">
              <div class="opp-info">
                <div class="opp-name">{{ opp.name }}</div>
                <div class="opp-org">{{ opp.org_name }}</div>
              </div>
              <div class="opp-amount">¥{{ formatAmount(opp.amount) }}</div>
              <el-tag size="small" :type="getStageType(opp.stage)">{{ getStageLabel(opp.stage) }}</el-tag>
            </div>
          </div>
          <el-empty v-else description="暂无商机" :image-size="60" />
        </el-card>

        <el-card shadow="never" class="list-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><Document /></el-icon>合同与发票</span>
              <div class="header-actions">
                <el-button link type="primary" size="small" @click="$router.push('/contract')">合同</el-button>
                <el-button link type="primary" size="small" @click="$router.push('/invoice')">发票</el-button>
              </div>
            </div>
          </template>
          <div class="contract-invoice-stats">
            <div class="ci-stat">
              <div class="ci-value">{{ stats.contracts }}</div>
              <div class="ci-label">合同数</div>
            </div>
            <div class="ci-stat">
              <div class="ci-value text-success">¥{{ formatAmount(stats.sales_contract_amount) }}</div>
              <div class="ci-label">销售合同</div>
            </div>
            <div class="ci-stat">
              <div class="ci-value text-danger">¥{{ formatAmount(stats.purchase_contract_amount) }}</div>
              <div class="ci-label">采购合同</div>
            </div>
            <div class="ci-stat">
              <div class="ci-value text-warning">¥{{ formatAmount(stats.contract_amount) }}</div>
              <div class="ci-label">合同总额</div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Bell, Clock, TrendCharts, Document, OfficeBuilding, User, Folder, Money, Check, Warning } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { request } from '@/api/request'
import dayjs from 'dayjs'
import * as echarts from 'echarts'

const router = useRouter()
const userStore = useUserStore()

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '早上好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

const currentDate = computed(() => dayjs().format('YYYY年MM月DD日 dddd'))
const userName = computed(() => userStore.userInfo?.name || '用户')

const stats = ref({
  organizations: 0,
  contacts: 0,
  deals: 0,
  deal_amount: 0,
  contracts: 0,
  contract_amount: 0,
  invoices: 0,
  invoice_amount: 0,
  followup_count: 0
})

const recentCustomers = ref<any[]>([])
const recentActivities = ref<any[]>([])
const todayFollowups = ref<any[]>([])
const recentOpportunities = ref<any[]>([])
const opportunityStats = ref<any>({ total: 0, won: 0, lost: 0 })
const funnelData = ref<any[]>([])

const funnelPeriod = ref('month')
const funnelChartRef = ref()

const statCards = computed(() => [
  { key: 'customers', label: '客户总数', value: stats.value.organizations, icon: OfficeBuilding, color: '#409EFF', bgColor: 'rgba(64, 158, 255, 0.1)' },
  { key: 'contacts', label: '联系人', value: stats.value.contacts, icon: User, color: '#67C23A', bgColor: 'rgba(103, 194, 58, 0.1)' },
  { key: 'deals', label: '进行中商机', value: stats.value.deals, sub: `¥${formatAmount(stats.value.deal_amount)}`, icon: TrendCharts, color: '#E6A23C', bgColor: 'rgba(230, 162, 60, 0.1)' },
  { key: 'contracts', label: '合同总额', value: `¥${formatAmount(stats.value.contract_amount)}`, sub: `销售¥${formatAmount(stats.value.sales_contract_amount)} / 采购¥${formatAmount(stats.value.purchase_contract_amount)}`, icon: Document, color: '#F56C6C', bgColor: 'rgba(245, 108, 108, 0.1)' }
])

const customerSummary = computed(() => [
  { label: '客户总数', value: stats.value.organizations },
  { label: '联系人', value: stats.value.contacts },
  { label: '待跟进', value: stats.value.followup_count }
])

function formatAmount(amount: number): string {
  if (!amount) return '0'
  if (amount >= 10000) return (amount / 10000).toFixed(1) + '万'
  return amount.toFixed(0)
}

function formatTime(date: string) {
  if (!date) return ''
  return dayjs(date).format('MM/DD HH:mm')
}

function getCustomerType(type: string) {
  const map: Record<string, string> = { final_customer: 'success', partner: 'warning', undecided: 'info' }
  return map[type] || 'info'
}

function getCustomerTypeLabel(type: string) {
  const map: Record<string, string> = { final_customer: '最终客户', partner: '合作伙伴', undecided: '未决定' }
  return map[type] || '未知'
}

function getStageType(stage: string) {
  const map: Record<string, string> = { business_driven: 'info', needs_defined: 'primary', evaluation: 'warning', procurement: 'danger', contract_signed: 'success', payment_implementation: 'success', closed_won: 'success', closed_lost: 'info' }
  return map[stage] || 'info'
}

function getStageLabel(stage: string) {
  const map: Record<string, string> = { business_driven: '①业务驱动', needs_defined: '②确定需求', evaluation: '③评估方案', procurement: '④落实采购', contract_signed: '⑤签订合同', payment_implementation: '⑥付款实施', closed_won: '赢单', closed_lost: '输单' }
  return map[stage] || stage
}

function getActivityType(type: string) {
  const map: Record<string, string> = { meeting: 'primary', call: 'success', email: 'warning', visit: 'danger' }
  return map[type] || 'info'
}

function getFollowupType(type: string) {
  const map: Record<string, string> = { call: 'success', meeting: 'primary', visit: 'warning', email: 'info' }
  return map[type] || 'info'
}

async function toggleFollowup(item: any) {
  try {
    await request.put(`/followups/${item.id}`, { done: !item.done })
    item.done = !item.done
    if (item.done) {
      ElMessage.success('已标记完成')
    }
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

async function fetchDashboard() {
  try {
    const res = await request.get('/dashboard')
    stats.value = res.stats || {}
    
    // 客户列表
    const customerRes = await request.get('/customers?page=1&pageSize=5')
    recentCustomers.value = customerRes.items || []
    
    // 活动列表
    const activityRes = await request.get('/activities?page=1&pageSize=5')
    recentActivities.value = activityRes.items || []
    
    // 待办列表
    const followupRes = await request.get('/followups?page=1&pageSize=10&done=0')
    todayFollowups.value = (followupRes.items || []).filter((f: any) => {
      if (!f.due_date) return false
      return dayjs(f.due_date).isSame(dayjs(), 'day')
    }).slice(0, 5)
    
    // 商机列表
    const oppRes = await request.get('/opportunities?page=1&pageSize=5')
    recentOpportunities.value = oppRes.items || []
    
    // 商机统计
    opportunityStats.value = {
      total: stats.value.deals || 0,
      won: 0,
      lost: 0
    }
    
    // 漏斗数据
    funnelData.value = res.funnel_data || []
    renderFunnelChart()
  } catch (e) {
    console.error('获取仪表盘数据失败', e)
  }
}

function renderFunnelChart() {
  nextTick(() => {
    if (!funnelChartRef.value) return
    const chart = echarts.init(funnelChartRef.value)
    const stages = ['①业务驱动、定位问题', '②确定需求、启动项目', '③评估方案、圈定供应商', '④制定规则、落实采购', '⑤得到结果、签订合同', '赢单']
    const data = funnelData.value.length > 0 
      ? funnelData.value.map((d: any, i: number) => ({ name: d.Name || stages[i], value: d.value || 0 }))
      : stages.map((name, i) => ({ name, value: 0 }))
    
    chart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c}' },
      color: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399'],
      series: [{
        type: 'funnel',
        left: '10%',
        top: 20,
        bottom: 20,
        width: '80%',
        minSize: '0%',
        maxSize: '100%',
        sort: 'descending',
        gap: 2,
        label: { show: true, position: 'inside', formatter: '{b}: {c}' },
        data
      }]
    })
  })
}

onMounted(() => {
  fetchDashboard()
  window.addEventListener('resize', () => {
    if (funnelChartRef.value) {
      echarts.getInstanceByDom(funnelChartRef.value)?.resize()
    }
  })
})
</script>

<style scoped lang="scss">
.dashboard-page {
  padding: 20px;
  background: #F5F7FA;
  min-height: 100%;
}

.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  .welcome-text h2 {
    margin: 0;
    font-size: 24px;
    font-weight: 600;
    color: #303133;
  }
  
  .sub-text {
    margin: 4px 0 0;
    color: #909399;
    font-size: 14px;
  }
}

.stat-card-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
  
  @media (max-width: 1200px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  }
  
  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  
  .stat-info {
    flex: 1;
    min-width: 0;
    
    .stat-value {
      font-size: 24px;
      font-weight: 700;
      color: #303133;
    }
    
    .stat-label {
      font-size: 13px;
      color: #909399;
      margin-top: 4px;
    }
  }
  
  .stat-sub {
    font-size: 12px;
    color: #67C23A;
    font-weight: 500;
  }
}

.chart-grid {
  margin-bottom: 20px;
  
  .chart-card {
    border-radius: 12px;
    border: none;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 600;
    }
    
    .funnel-chart {
      height: 260px;
    }
  }
}

.main-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  
  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
  }
}

.left-column, .right-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.list-card {
  border-radius: 12px;
  border: none;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
    
    .el-icon {
      margin-right: 6px;
    }
    
    .header-actions {
      display: flex;
      gap: 8px;
    }
  }
}

.todo-list {
  .todo-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid #F0F2F5;
    
    &:last-child { border-bottom: none; }
    
    .todo-content {
      flex: 1;
      min-width: 0;
      
      .todo-title {
        font-size: 14px;
        color: #303133;
      }
      
      .todo-org {
        font-size: 12px;
        color: #909399;
      }
    }
  }
}

.activity-item {
  .activity-title {
    font-size: 14px;
    font-weight: 500;
    color: #303133;
  }
  
  .activity-desc {
    font-size: 12px;
    color: #606266;
    margin-top: 2px;
  }
  
  .activity-meta {
    font-size: 12px;
    color: #909399;
    margin-top: 2px;
  }
}

.customer-summary {
  display: flex;
  gap: 24px;
  padding: 12px 0;
  border-bottom: 1px solid #F0F2F5;
  margin-bottom: 12px;
  
  .summary-item {
    display: flex;
    flex-direction: column;
    
    .summary-value {
      font-size: 20px;
      font-weight: 700;
      color: #303133;
    }
    
    .summary-label {
      font-size: 12px;
      color: #909399;
    }
  }
}

.customer-list {
  .customer-item {
    padding: 8px 0;
    border-bottom: 1px solid #F0F2F5;
    
    &:last-child { border-bottom: none; }
    
    .customer-info {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .customer-name {
        font-size: 14px;
        font-weight: 500;
        color: #303133;
      }
    }
    
    .customer-meta {
      font-size: 12px;
      color: #909399;
      margin-top: 2px;
    }
  }
}

.opportunity-stats {
  display: flex;
  gap: 24px;
  padding: 12px 0;
  border-bottom: 1px solid #F0F2F5;
  margin-bottom: 12px;
  
  .opp-stat {
    display: flex;
    flex-direction: column;
    
    .opp-value {
      font-size: 20px;
      font-weight: 700;
      color: #303133;
      
      &.text-success { color: #67C23A; }
      &.text-danger { color: #F56C6C; }
    }
    
    .opp-label {
      font-size: 12px;
      color: #909399;
    }
  }
}

.opportunity-list {
  .opp-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
    border-bottom: 1px solid #F0F2F5;
    
    &:last-child { border-bottom: none; }
    
    .opp-info {
      flex: 1;
      min-width: 0;
      
      .opp-name {
        font-size: 14px;
        font-weight: 500;
        color: #303133;
      }
      
      .opp-org {
        font-size: 12px;
        color: #909399;
      }
    }
    
    .opp-amount {
      font-size: 14px;
      font-weight: 600;
      color: #E6A23C;
    }
  }
}

.contract-invoice-stats {
  display: flex;
  gap: 24px;
  padding: 8px 0;
  
  .ci-stat {
    display: flex;
    flex-direction: column;
    
    .ci-value {
      font-size: 18px;
      font-weight: 700;
      color: #303133;
      
      &.text-warning { color: #E6A23C; }
    }
    
    .ci-label {
      font-size: 12px;
      color: #909399;
    }
  }
}
</style>
