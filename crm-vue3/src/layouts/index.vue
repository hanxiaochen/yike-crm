<template>
  <div class="app-wrapper">
    <!-- 侧边栏 -->
    <Sidebar class="sidebar-container" :class="{ 'is-collapse': isCollapse }" />

    <!-- 主内容区 -->
    <div class="main-container" :class="{ 'is-collapse': isCollapse }">
      <!-- 顶部导航 -->
      <Navbar />

      <!-- 标签页 -->
      <TagsView />

      <!-- 内容区 -->
      <AppMain />

      <!-- 底部版权 -->
      <div class="app-footer">
        © 2026 奇智科技（北京）有限公司 版权所有
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, provide } from 'vue'
import Sidebar from './components/Sidebar.vue'
import Navbar from './components/Navbar.vue'
import TagsView from './components/TagsView.vue'
import AppMain from './components/AppMain.vue'

// 侧边栏折叠状态
const isCollapse = ref(false)

function toggleSideBar() {
  isCollapse.value = !isCollapse.value
}

// Provide to child components
provide('isCollapse', isCollapse)
provide('toggleSideBar', toggleSideBar)
</script>

<style scoped lang="scss">
.app-wrapper {
  display: flex;
  height: 100vh;
  width: 100%;
}

.sidebar-container {
  width: 220px;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 1001;
  overflow: hidden;
  background: #304156;
  transition: width 0.3s;

  &.is-collapse {
    width: 64px;
  }
}

.main-container {
  flex: 1;
  margin-left: 220px;
  min-height: 100vh;
  transition: margin-left 0.3s;
  display: flex;
  flex-direction: column;

  &.is-collapse {
    margin-left: 64px;
  }
}

.app-footer {
  padding: 12px 20px;
  text-align: center;
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  border-top: 1px solid #e4e7ed;
  flex-shrink: 0;
}

// 响应式布局 - 小屏幕（平板）
@media screen and (max-width: 1024px) {
  .sidebar-container {
    width: 64px;
  }
  
  .main-container {
    margin-left: 64px;
  }
}

// 响应式布局 - 手机
@media screen and (max-width: 768px) {
  .sidebar-container {
    width: 0;
    overflow: hidden;
  }
  
  .main-container {
    margin-left: 0;
  }
}
</style>
