<template>
  <div class="navbar">
    <!-- 左侧 -->
    <div class="navbar-left">
      <hamburger 
        :is-active="isCollapse" 
        class="hamburger"
        @toggle="handleToggle"
      />
      <breadcrumb class="breadcrumb" />
    </div>
    
    <!-- 右侧 -->
    <div class="navbar-right">
      <!-- 搜索 -->
      <search class="navbar-search" />
      
      <!-- 全屏 -->
      <screenfull class="navbar-item" />
      
      <!-- 通知 -->
      <el-badge :value="3" class="navbar-item">
        <bell class="navbar-icon" />
      </el-badge>
      
      <!-- 用户下拉 -->
      <el-dropdown trigger="click" @command="handleCommand">
        <div class="user-dropdown">
          <img :src="userAvatar" alt="avatar" class="user-avatar" />
          <span class="user-name">{{ userName }}</span>
          <arrow-down class="dropdown-arrow" />
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>
              个人中心
            </el-dropdown-item>
            <el-dropdown-item command="password">
              <el-icon><Lock /></el-icon>
              修改密码
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessageBox } from 'element-plus'
import { User, Setting, SwitchButton, Bell, ArrowDown, Lock } from '@element-plus/icons-vue'
import Hamburger from '@/components/Hamburger.vue'

const router = useRouter()
const userStore = useUserStore()

const isCollapse = inject('isCollapse', ref(false)) as ReturnType<typeof ref<boolean>>
const toggleSideBar = inject('toggleSideBar', () => {}) as () => void

const userName = computed(() => userStore.userInfo?.name || '用户')
const userAvatar = computed(() => userStore.userInfo?.avatar || '/avatar.svg')

function handleToggle() {
  toggleSideBar()
}

function handleCommand(command: string) {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'password':
      router.push('/password')
      break
    case 'logout':
      handleLogout()
      break
  }
}

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await userStore.logout()
    router.push('/login')
  } catch {
    // 取消操作
  }
}
</script>

<style scoped lang="scss">
.navbar {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  position: relative;
  z-index: 1000;

  .navbar-left {
    display: flex;
    align-items: center;
    gap: 16px;
    
    .hamburger {
      display: flex;
      align-items: center;
      cursor: pointer;
    }
    
    .breadcrumb {
      display: flex;
      align-items: center;
    }
  }

  .navbar-right {
    display: flex;
    align-items: center;
    gap: 16px;
    
    .navbar-item {
      display: flex;
      align-items: center;
      cursor: pointer;
      padding: 0 8px;
    }
    
    .navbar-icon {
      font-size: 20px;
      color: #606266;
    }

    .user-dropdown {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 0 8px;
      cursor: pointer;
      
      .user-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
      }
      
      .user-name {
        font-size: 14px;
        color: #606266;
        white-space: nowrap;
      }
      
      .dropdown-arrow {
        font-size: 10px;
        color: #909399;
      }
    }
  }
}
</style>
