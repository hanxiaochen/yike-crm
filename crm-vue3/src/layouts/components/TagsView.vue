<template>
  <div class="tags-view-container">
    <scroll-panel class="tags-view-wrapper">
      <router-link
        v-for="tag in visitedViews"
        :key="tag.path"
        :to="{ path: tag.path, query: tag.query }"
        class="tags-view-item"
        :class="{ active: isActive(tag) }"
        @contextmenu.prevent="openMenu(tag, $event)"
      >
        {{ tag.title }}
        <span 
          v-if="!isAffix(tag)" 
          class="close-icon"
          @click.prevent.stop="closeSelectedTag(tag)"
        >
          <el-icon><Close /></el-icon>
        </span>
      </router-link>
    </scroll-panel>
    
    <!-- 右键菜单 -->
    <ul 
      v-show="visible" 
      class="contextmenu"
      :style="{ left: left + 'px', top: top + 'px' }"
    >
      <li @click="refreshSelectedTag(selectedTag)">刷新</li>
      <li @click="closeSelectedTag(selectedTag)">关闭</li>
      <li @click="closeOthersTags">关闭其他</li>
      <li @click="closeAllTags">关闭所有</li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const visitedViews = ref([
  { path: '/dashboard', title: '仪表盘', query: {} },
  { path: '/customer/list', title: '客户列表', query: {} }
])

const visible = ref(false)
const top = ref(0)
const left = ref(0)
const selectedTag = ref({ path: '', title: '', query: {} as any })

function isActive(tag: any) {
  return tag.path === route.path
}

function isAffix(tag: any) {
  return tag.path === '/dashboard'
}

function openMenu(tag: any, event: MouseEvent) {
  visible.value = true
  left.value = event.clientX
  top.value = event.clientY
  selectedTag.value = tag
}

function closeSelectedTag(tag: any) {
  // Remove the tag from visitedViews
  const index = visitedViews.value.findIndex(v => v.path === tag.path)
  if (index !== -1) {
    visitedViews.value.splice(index, 1)
  }
  // If closing current route, navigate to last view
  if (route.path === tag.path) {
    const lastView = visitedViews.value[visitedViews.value.length - 1]
    if (lastView) {
      router.push(lastView.path)
    }
  }
  visible.value = false
}

function refreshSelectedTag(tag: any) {
  visible.value = false
}

function closeOthersTags() {
  visible.value = false
}

function closeAllTags() {
  visible.value = false
}
</script>

<style scoped lang="scss">
.tags-view-container {
  height: 40px;
  background: #fff;
  border-bottom: 1px solid #d8dce5;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.12);
  
  .tags-view-wrapper {
    .tags-view-item {
      display: inline-flex;
      align-items: center;
      padding: 0 12px;
      height: 34px;
      margin-top: 4px;
      margin-left: 4px;
      font-size: 12px;
      color: #495057;
      background: #fff;
      border: 1px solid #d8dce5;
      border-radius: 4px;
      text-decoration: none;
      cursor: pointer;
      transition: all 0.3s;
      
      &:first-child {
        margin-left: 0;
      }
      
      &:hover {
        color: #409EFF;
        border-color: #409EFF;
      }
      
      &.active {
        color: #fff;
        background: #409EFF;
        border-color: #409EFF;
        
        .close-icon {
          color: #fff;
        }
      }
      
      .close-icon {
        margin-left: 6px;
        font-size: 10px;
        vertical-align: middle;
        
        &:hover {
          color: #fff;
          background: rgba(255, 255, 255, 0.3);
          border-radius: 50%;
        }
      }
    }
  }
  
  .contextmenu {
    position: absolute;
    margin: 0;
    padding: 4px 0;
    background: #fff;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    z-index: 2000;
    list-style: none;
    
    li {
      padding: 8px 16px;
      font-size: 12px;
      cursor: pointer;
      
      &:hover {
        background: #f5f7fa;
        color: #409EFF;
      }
    }
  }
}
</style>
