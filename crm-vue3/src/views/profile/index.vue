<template>
  <div class="profile-page">
    <div class="profile-container">
      <!-- 左侧用户信息卡片 -->
      <div class="profile-card">
        <div class="avatar-section">
          <div class="avatar-wrapper">
            <el-avatar :size="80" :src="avatarUrl">
              <el-icon :size="40"><UserFilled /></el-icon>
            </el-avatar>
          </div>
          <div class="user-info">
            <h2 class="username">{{ userInfo.name || userInfo.username }}</h2>
            <el-tag size="small" type="primary">{{ roleLabel }}</el-tag>
          </div>
        </div>
        <div class="profile-stats">
          <div class="stat-item">
            <span class="stat-value">{{ userInfo.username }}</span>
            <span class="stat-label">用户名</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ userInfo.email || '-' }}</span>
            <span class="stat-label">邮箱</span>
          </div>
        </div>
      </div>

      <!-- 右侧菜单列表 -->
      <div class="profile-menu">
        <div class="menu-item" @click="activeMenu = 'password'">
          <div class="menu-icon">
            <el-icon><Lock /></el-icon>
          </div>
          <div class="menu-content">
            <div class="menu-title">修改密码</div>
            <div class="menu-desc">修改账户登录密码</div>
          </div>
          <div class="menu-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>

        <div class="menu-item" @click="activeMenu = 'about'">
          <div class="menu-icon">
            <el-icon><InfoFilled /></el-icon>
          </div>
          <div class="menu-content">
            <div class="menu-title">关于易客CRM</div>
            <div class="menu-desc">版本信息与技术支持</div>
          </div>
          <div class="menu-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>

        <div class="menu-item logout" @click="handleLogout">
          <div class="menu-icon">
            <el-icon><SwitchButton /></el-icon>
          </div>
          <div class="menu-content">
            <div class="menu-title">退出登录</div>
            <div class="menu-desc">退出当前账户</div>
          </div>
          <div class="menu-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </div>

      <!-- 底部版权 -->
      <div class="profile-footer">
        © 2026 奇智科技（北京）有限公司 版权所有
      </div>
    </div>

    <!-- 修改密码弹窗 -->
    <el-dialog v-model="showPasswordDialog" title="修改密码" width="420px" :close-on-click-modal="false">
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="90px">
        <el-form-item label="当前密码" prop="oldPassword">
          <el-input v-model="pwdForm.oldPassword" type="password" show-password placeholder="请输入当前密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="pwdForm.newPassword" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="pwdForm.confirmPassword" type="password" show-password placeholder="请确认新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" @click="handleChangePwd" :loading="pwdLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 关于弹窗 -->
    <el-dialog v-model="showAboutDialog" title="关于易客CRM" width="400px">
      <div class="about-content">
        <div class="about-logo">
          <h2>易客CRM</h2>
          <p class="version">版本 1.0.0</p>
        </div>
        <div class="about-desc">
          <p>智能化客户关系管理平台</p>
          <p>帮助企业高效管理客户全生命周期</p>
        </div>
        <div class="about-company">
          <p>© 2026 奇智科技（北京）有限公司</p>
          <p>版权所有</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UserFilled, Lock, InfoFilled, ArrowRight, SwitchButton } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { request } from '@/api/request'

const router = useRouter()
const userStore = useUserStore()

const activeMenu = ref('')
const showPasswordDialog = ref(false)
const showAboutDialog = ref(false)
const pwdLoading = ref(false)
const pwdFormRef = ref()

const pwdForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value !== pwdForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const pwdRules = {
  oldPassword: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const userInfo = computed(() => userStore.userInfo || {})

const roleLabel = computed(() => {
  const role = userInfo.value?.role
  if (role === 1 || role === 'admin') return '管理员'
  if (role === 2 || role === 'user') return '普通用户'
  return '未知'
})

const avatarUrl = computed(() => {
  // 如果有头像URL则使用，否则使用默认
  return userInfo.value?.avatar || ''
})

onMounted(() => {
  loadUserInfo()
})

function loadUserInfo() {
  // 用户信息已通过 store 获取
}

async function handleChangePwd() {
  if (!pwdFormRef.value) return
  await pwdFormRef.value.validate(async (valid) => {
    if (!valid) return
    pwdLoading.value = true
    try {
      await request.post(`/users/${userInfo.value?.id}/change-password`, {
        old_password: pwdForm.oldPassword,
        new_password: pwdForm.newPassword
      })
      ElMessage.success('密码修改成功')
      showPasswordDialog.value = false
      pwdForm.oldPassword = ''
      pwdForm.newPassword = ''
      pwdForm.confirmPassword = ''
    } catch (e: any) {
      ElMessage.error(e?.message || '密码修改失败')
    } finally {
      pwdLoading.value = false
    }
  })
}

function handleLogout() {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    router.push('/login')
    ElMessage.success('已退出登录')
  }).catch(() => {})
}
</script>

<style scoped lang="scss">
.profile-page {
  min-height: calc(100vh - 100px);
  background: #F5F7FA;
  padding: 20px;
}

.profile-container {
  max-width: 800px;
  margin: 0 auto;
}

.profile-card {
  background: #fff;
  border-radius: 12px;
  padding: 32px;
  margin-bottom: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
  padding-bottom: 24px;
  border-bottom: 1px solid #EBEEF5;
  margin-bottom: 20px;

  .avatar-wrapper {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 32px;
    overflow: hidden;

    :deep(.el-avatar) {
      width: 100%;
      height: 100%;
    }
  }

  .user-info {
    .username {
      margin: 0 0 8px;
      font-size: 24px;
      font-weight: 600;
      color: #303133;
    }

    .el-tag {
      font-size: 12px;
    }
  }
}

.profile-stats {
  display: flex;
  gap: 40px;

  .stat-item {
    display: flex;
    flex-direction: column;
    gap: 4px;

    .stat-value {
      font-size: 14px;
      color: #303133;
      font-weight: 500;
    }

    .stat-label {
      font-size: 12px;
      color: #909399;
    }
  }
}

.profile-menu {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);

  .menu-item {
    display: flex;
    align-items: center;
    padding: 16px 20px;
    cursor: pointer;
    transition: background 0.2s;
    border-bottom: 1px solid #EBEEF5;

    &:last-child {
      border-bottom: none;
    }

    &:hover {
      background: #F5F7FA;
    }

    &.logout {
      .menu-icon {
        background: #F56C6C20;
        color: #F56C6C;
      }
      .menu-title {
        color: #F56C6C;
      }
    }

    .menu-icon {
      width: 40px;
      height: 40px;
      border-radius: 10px;
      background: #667eea20;
      color: #667eea;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      margin-right: 16px;
    }

    .menu-content {
      flex: 1;

      .menu-title {
        font-size: 15px;
        font-weight: 500;
        color: #303133;
        margin-bottom: 2px;
      }

      .menu-desc {
        font-size: 12px;
        color: #909399;
      }
    }

    .menu-arrow {
      color: #C0C4CC;
      font-size: 14px;
    }
  }
}

.profile-footer {
  text-align: center;
  padding: 24px;
  font-size: 12px;
  color: #909399;
}

.about-content {
  text-align: center;
  padding: 20px 0;

  .about-logo {
    margin-bottom: 20px;

    h2 {
      margin: 0 0 8px;
      font-size: 24px;
      font-weight: 600;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .version {
      margin: 0;
      font-size: 13px;
      color: #909399;
    }
  }

  .about-desc {
    margin-bottom: 24px;

    p {
      margin: 4px 0;
      font-size: 14px;
      color: #606266;
    }
  }

  .about-company {
    padding-top: 16px;
    border-top: 1px solid #EBEEF5;

    p {
      margin: 4px 0;
      font-size: 12px;
      color: #909399;
    }
  }
}
</style>
