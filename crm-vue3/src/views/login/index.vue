<template>
  <div class="login-container">
    <div class="login-box">
      <!-- 左侧装饰 -->
      <div class="login-left">
        <div class="login-intro">
          <h1>易客CRM</h1>
          <p>智能化客户关系管理平台</p>
          <ul class="feature-list">
            <li>
              <el-icon><Check /></el-icon>
              客户全生命周期管理
            </li>
            <li>
              <el-icon><Check /></el-icon>
              销售流程可视化追踪
            </li>
            <li>
              <el-icon><Check /></el-icon>
              智能数据分析洞察
            </li>
            <li>
              <el-icon><Check /></el-icon>
              团队协作效率提升
            </li>
          </ul>
        </div>
      </div>
      
      <!-- 右侧登录表单 -->
      <div class="login-right">
        <div class="login-form-wrapper">
          <h2 class="form-title">账号登录</h2>
          
          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            class="login-form"
            @submit.prevent="handleLogin"
          >
            <el-form-item prop="username">
              <el-input 
                v-model="form.username"
                placeholder="请输入用户名"
                size="large"
                prefix-icon="User"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                prefix-icon="Lock"
                show-password
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            
            <el-form-item>
              <div class="form-options">
                <el-checkbox v-model="form.remember">记住密码</el-checkbox>
                <a href="#" class="forgot-link">忘记密码？</a>
              </div>
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="loading"
                class="login-button"
                @click="handleLogin"
              >
                登 录
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>
    <!-- 版权信息 -->
    <div class="login-copyright">
      © 2026 奇智科技（北京）有限公司 版权所有
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  remember: false
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
}

async function handleLogin() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      await userStore.login({
        username: form.username,
        password: form.password
      })
      ElMessage.success('登录成功')
      router.push('/dashboard')
    } catch (error: any) {
      // 显示登录失败的详细错误信息
      const errorMsg = error?.response?.data?.message || error?.message || '登录失败，请检查用户名和密码'
      ElMessage.error(errorMsg)
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped lang="scss">
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  display: flex;
  width: 900px;
  height: 540px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  position: relative;
}

.login-copyright {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
  white-space: nowrap;
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  
  .login-intro {
    color: #fff;
    
    h1 {
      font-size: 32px;
      font-weight: 700;
      margin-bottom: 12px;
    }
    
    p {
      font-size: 16px;
      opacity: 0.9;
      margin-bottom: 40px;
    }
    
    .feature-list {
      list-style: none;
      padding: 0;
      margin: 0;
      
      li {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
        font-size: 15px;
        
        .el-icon {
          font-size: 18px;
        }
      }
    }
  }
}

.login-right {
  width: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  
  .login-form-wrapper {
    width: 100%;
    max-width: 320px;
    
    .form-title {
      font-size: 24px;
      font-weight: 600;
      color: #303133;
      text-align: center;
      margin-bottom: 32px;
    }
    
    .login-form {
      .form-options {
        width: 100%;
        display: flex;
        justify-content: space-between;
        align-items: center;
        
        .forgot-link {
          font-size: 14px;
          color: #409EFF;
          
          &:hover {
            color: #66b1ff;
          }
        }
      }
      
      .login-button {
        width: 100%;
        height: 48px;
        font-size: 16px;
        border-radius: 8px;
      }
    }
  }
}
</style>
