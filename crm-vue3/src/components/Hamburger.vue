<template>
  <el-icon :size="20" @click="$emit('toggle')">
    <Expand v-if="isActive" />
    <Fold v-else />
  </el-icon>
</template>

<script setup lang="ts">
import { Expand, Fold } from '@element-plus/icons-vue'
defineProps<{
  isActive?: boolean
}>()
defineEmits(['toggle'])
</script>
