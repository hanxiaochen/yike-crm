<template>
  <div class="sidebar-wrapper">
    <!-- Logo区域 -->
    <div class="sidebar-logo">
      <img src="/logo.svg" alt="logo" class="logo-img" v-if="showLogo" />
      <span class="logo-text" v-if="!isCollapse">易客CRM</span>
    </div>
    
    <!-- 菜单 -->
    <el-menu
      :default-active="activeMenu"
      :collapse="isCollapse"
      :collapse-transition="false"
      :unique-opened="true"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
      router
    >
      <el-menu-item index="/dashboard">
        <el-icon><DataAnalysis /></el-icon>
        <template #title>仪表盘</template>
      </el-menu-item>
      
      <el-sub-menu index="/customer">
        <template #title>
          <el-icon><OfficeBuilding /></el-icon>
          <span>客户管理</span>
        </template>
        <el-menu-item index="/customer/list">客户列表</el-menu-item>
        <el-menu-item index="/customer/contact">联系人</el-menu-item>
      </el-sub-menu>
      
      <el-sub-menu index="/opportunity">
        <template #title>
          <el-icon><Money /></el-icon>
          <span>商机管理</span>
        </template>
        <el-menu-item index="/opportunity/list">商机列表</el-menu-item>
        <el-menu-item index="/opportunity/kanban">商机看板</el-menu-item>
      </el-sub-menu>
      
      <el-menu-item index="/contract">
        <el-icon><Document /></el-icon>
        <template #title>合同管理</template>
      </el-menu-item>
      
      <el-menu-item index="/invoice">
        <el-icon><Coin /></el-icon>
        <template #title>发票管理</template>
      </el-menu-item>
      
      <el-menu-item index="/activity">
        <el-icon><Calendar /></el-icon>
        <template #title>活动记录</template>
      </el-menu-item>
      
      <el-menu-item index="/followup">
        <el-icon><Tickets /></el-icon>
        <template #title>待办跟进</template>
      </el-menu-item>
      
      <el-menu-item index="/statistics">
        <el-icon><DataLine /></el-icon>
        <template #title>数据分析</template>
      </el-menu-item>
      
      <el-sub-menu index="/system">
        <template #title>
          <el-icon><Setting /></el-icon>
          <span>系统管理</span>
        </template>
        <el-menu-item index="/system/user">用户管理</el-menu-item>
        <el-menu-item index="/system/role">角色管理</el-menu-item>
      </el-sub-menu>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { computed, inject } from 'vue'
import { useRoute } from 'vue-router'

import { 
  DataAnalysis, 
  OfficeBuilding, 
  UserFilled, 
  Money, 
  Document, 
  Calendar, 
  Tickets, 
  DataLine,
  Setting,
  Coin 
} from '@element-plus/icons-vue'

const route = useRoute()

const isCollapse = inject('isCollapse', ref(false)) as ReturnType<typeof ref<boolean>>
// If injected is a Ref, use it directly; if it's a raw value, wrap it
const collapseValue = computed(() => {
  const val = isCollapse
  return val instanceof Function ? false : (val.value ?? val)
})
const showLogo = computed(() => true)

const activeMenu = computed(() => route.path)
</script>

<style scoped lang="scss">
.sidebar-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .sidebar-logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    border-bottom: 1px solid #3d4a5c;
    
    .logo-img {
      width: 32px;
      height: 32px;
    }
    
    .logo-text {
      font-size: 18px;
      font-weight: 600;
      color: #fff;
      white-space: nowrap;
    }
  }
  
  .el-menu {
    flex: 1;
    border-right: none;
    overflow-y: auto;
    overflow-x: hidden;
  }
  
  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    height: 50px;
    line-height: 50px;
    
    &:hover {
      background: #263445 !important;
    }
  }
  
  :deep(.el-menu-item.is-active) {
    background: #263445 !important;
  }
}
</style>
