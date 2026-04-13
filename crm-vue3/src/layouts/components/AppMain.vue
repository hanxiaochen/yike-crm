<template>
  <main class="app-main">
    <router-view v-slot="{ Component }">
      <transition name="fade-transform" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </main>
</template>

<script setup lang="ts">
</script>

<style scoped lang="scss">
.app-main {
  flex: 1;
  padding: 16px;
  background: #F5F7FA;
}

// 路由动画
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter-from,
.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
