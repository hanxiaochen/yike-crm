<template>
  <div class="statistics-page">
    <el-row :gutter="16" class="stat-row">
      <el-col :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-label">客户总数</div>
          <div class="stat-value">156</div>
          <div class="stat-trend up">↑ 12%</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-label">商机金额</div>
          <div class="stat-value">¥1280万</div>
          <div class="stat-trend up">↑ 8%</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-label">合同金额</div>
          <div class="stat-value">¥890万</div>
          <div class="stat-trend up">↑ 15%</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-label">回款率</div>
          <div class="stat-value">78%</div>
          <div class="stat-trend down">↓ 3%</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="chart-row">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><span>商机漏斗</span></template>
          <div ref="funnelChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><span>销售趋势</span></template>
          <div ref="trendChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="chart-row">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><span>客户行业分布</span></template>
          <div ref="industryChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><span>团队业绩排名</span></template>
          <el-table :data="teamRanking" style="width: 100%">
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="deals" label="商机数" width="100" />
            <el-table-column prop="amount" label="金额" />
            <el-table-column label="排名" width="80">
              <template #default="{ $index }">
                <el-tag :type="$index === 0 ? 'warning' : ''">{{ $index + 1 }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const funnelChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()
const industryChartRef = ref<HTMLElement>()
let funnelChart: any = null
let trendChart: any = null
let industryChart: any = null

const teamRanking = [
  { name: '韩晓晨', deals: 12, amount: '¥320万' },
  { name: '张经理', deals: 10, amount: '¥280万' },
  { name: '王经理', deals: 8, amount: '¥190万' }
]

function initCharts() {
  if (funnelChartRef.value) {
    funnelChart = echarts.init(funnelChartRef.value)
    funnelChart.setOption({
      tooltip: { trigger: 'item' },
      color: ['#5470C6', '#91CC75', '#FAC858', '#EE6666', '#73C0DE'],
      series: [{
        type: 'funnel',
        left: '10%',
        top: 20,
        bottom: 20,
        width: '80%',
        label: { show: true, position: 'inside', formatter: '{b}\n{c}', color: '#fff' },
        data: [
          { name: '初步接触', value: 50 },
          { name: '资格确认', value: 30 },
          { name: '方案报价', value: 15 },
          { name: '合同签订', value: 8 }
        ]
      }]
    })
  }

  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 50, right: 20, bottom: 30, top: 20 },
      xAxis: {
        type: 'category',
        data: ['1月', '2月', '3月', '4月', '5月', '6月'],
        axisLine: { show: false },
        axisTick: { show: false }
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { lineStyle: { type: 'dashed', color: '#E5E5E5' } }
      },
      series: [{
        type: 'line',
        data: [120, 200, 150, 280, 320, 450],
        smooth: true,
        lineStyle: { width: 3, color: '#409EFF' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64,158,255,0.3)' },
            { offset: 1, color: 'rgba(64,158,255,0.05)' }
          ])
        }
      }]
    })
  }

  if (industryChartRef.value) {
    industryChart = echarts.init(industryChartRef.value)
    industryChart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        data: [
          { name: '能源电力', value: 45 },
          { name: '金融银行', value: 25 },
          { name: '政府机构', value: 15 },
          { name: '其他', value: 15 }
        ]
      }]
    })
  }
}

onMounted(() => {
  initCharts()
})

onUnmounted(() => {
  funnelChart?.dispose()
  trendChart?.dispose()
  industryChart?.dispose()
})
</script>

<style scoped lang="scss">
.statistics-page {
  .stat-row {
    margin-bottom: 16px;
  }

  .stat-card {
    text-align: center;
    padding: 20px;

    .stat-label {
      font-size: 14px;
      color: #909399;
      margin-bottom: 8px;
    }

    .stat-value {
      font-size: 28px;
      font-weight: 700;
      color: #303133;
      margin-bottom: 8px;
    }

    .stat-trend {
      font-size: 13px;
      font-weight: 500;

      &.up {
        color: #67C23A;
      }

      &.down {
        color: #F56C6C;
      }
    }
  }

  .chart-row {
    margin-bottom: 16px;
  }
}
</style>
