<template>
  <div class="activity-page">
    <div class="search-bar">
      <div class="search-form">
        <el-select v-model="query.type" placeholder="活动类型" clearable style="width: 120px" @change="handleSearch">
          <el-option label="电话" value="call" />
          <el-option label="拜访" value="visit" />
          <el-option label="会议" value="meeting" />
          <el-option label="邮件" value="email" />
          <el-option label="其他" value="other" />
        </el-select>
        <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" style="width: 260px" @change="handleDateChange" />
      </div>
      <div class="action-buttons">
        <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon>记录活动</el-button>
      </div>
    </div>

    <el-card shadow="never" class="table-card">
      <el-timeline v-if="tableData.length > 0">
        <el-timeline-item v-for="item in tableData" :key="item.id" :timestamp="item.activity_date" :type="getTypeColor(item.type)" placement="top">
          <el-card shadow="never">
            <div class="activity-header">
              <el-tag size="small" :type="getTypeColor(item.type)">{{ getTypeLabel(item.type) }}</el-tag>
              <el-link type="primary" @click="handleViewOrg(item)">{{ item.org_name }}</el-link>
              <span class="contact-name" v-if="item.contact_name">- {{ item.contact_name }}</span>
            </div>
            <div class="activity-title">{{ item.title }}</div>
            <div class="activity-desc" v-if="item.description">{{ item.description }}</div>
            <div class="activity-footer">
              <span>记录人：{{ item.recorded_by }}</span>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无活动记录" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import dayjs from 'dayjs'

const query = reactive({ type: '', start_date: '', end_date: '' })
const dateRange = ref<any[]>([])
const tableData = ref<any[]>([])

const mockActivities = [
  { id: 1, type: 'call', activity_date: dayjs().format('YYYY-MM-DD HH:mm'), title: '电话沟通项目需求', description: '与张总电话沟通了智能运维平台的项目需求，对方表示4月份会有采购计划。', org_name: '华能集团', contact_name: '张总', recorded_by: '韩晓晨' },
  { id: 2, type: 'visit', activity_date: dayjs().subtract(1, 'day').format('YYYY-MM-DD HH:mm'), title: '拜访客户信息部', description: '拜访了国电集团信息部负责人李主任，了解了数据中心建设的整体规划。', org_name: '国电集团', contact_name: '李主任', recorded_by: '韩晓晨' },
  { id: 3, type: 'meeting', activity_date: dayjs().subtract(3, 'day').format('YYYY-MM-DD HH:mm'), title: '参加产品技术交流会', description: '参加了大唐发电组织的产品技术交流会，向客户展示了网盾产品的核心优势。', org_name: '大唐发电', contact_name: '王总', recorded_by: '韩晓晨' },
]

function handleSearch() {}
function handleDateChange() {}
function handleAdd() {}
function handleViewOrg(item: any) {}
function getTypeColor(type: string) {
  return { call: 'primary', visit: 'success', meeting: 'warning', email: 'info', other: '' }[type] || ''
}
function getTypeLabel(type: string) {
  return { call: '电话', visit: '拜访', meeting: '会议', email: '邮件', other: '其他' }[type] || type
}

onMounted(() => { tableData.value = mockActivities })
</script>

<style scoped lang="scss">
.activity-page {
  .activity-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    
    .contact-name { color: #606266; font-size: 14px; }
  }
  
  .activity-title { font-size: 15px; font-weight: 500; color: #303133; margin-bottom: 8px; }
  .activity-desc { font-size: 14px; color: #606266; line-height: 1.6; margin-bottom: 8px; }
  .activity-footer { font-size: 12px; color: #909399; }
}
</style>
