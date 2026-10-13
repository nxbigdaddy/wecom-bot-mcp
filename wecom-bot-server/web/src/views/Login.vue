<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <el-icon :size="48" color="#409EFF"><ChatDotRound /></el-icon>
        <h1>WeCom Bot Server</h1>
        <p>企业微信机器人管理系统</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        size="large"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <div class="login-options">
            <el-checkbox v-model="loginForm.remember">记住密码</el-checkbox>
            <el-link type="primary" :underline="false">忘记密码？</el-link>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
            style="width: 100%"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>

        <el-alert
          v-if="errorMessage"
          type="error"
          :title="errorMessage"
          :closable="false"
          show-icon
        />
      </el-form>

      <div class="login-footer">
        <p>默认账号：admin / admin123</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { ChatDotRound } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref(null)
const loading = ref(false)
const errorMessage = ref('')

const loginForm = reactive({
  username: '',
  password: '',
  remember: false
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      errorMessage.value = ''

      try {
        // 调用登录 API
        const response = await fetch('/api/v1/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: loginForm.username,
            password: YOUR_PASSWORD
          })
        })

        const data = await response.json()

        if (response.ok && data.access_token) {
          // 保存 token
          userStore.setToken(data.access_token)
          userStore.setUsername(data.username)
          userStore.setRole(data.role)

          ElMessage.success('登录成功')

          // 记住密码
          if (loginForm.remember) {
            localStorage.setItem('rememberedUser', loginForm.username)
          } else {
            localStorage.removeItem('rememberedUser')
          }

          // 跳转到首页
          setTimeout(() => {
            router.push('/')
          }, 500)
        } else {
          errorMessage.value = data.detail || '用户名或密码错误'
          ElMessage.error(errorMessage.value)
        }
      } catch (error) {
        console.error('登录失败:', error)
        errorMessage.value = '登录失败，请检查网络连接'
        ElMessage.error('登录失败，请检查网络连接')
      } finally {
        loading.value = false
      }
    }
  })
}

// 检查是否有记住的用户名
if (localStorage.getItem('rememberedUser')) {
  loginForm.username = localStorage.getItem('rememberedUser')
  loginForm.remember = true
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.login-container::before {
  content: '';
  position: absolute;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: backgroundMove 20s linear infinite;
}

@keyframes backgroundMove {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(50px, 50px);
  }
}

.login-box {
  background: white;
  border-radius: 16px;
  padding: 48px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  position: relative;
  z-index: 1;
  animation: slideIn 0.5s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h1 {
  color: #303133;
  font-size: 28px;
  font-weight: 600;
  margin: 16px 0 8px 0;
}

.login-header p {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.login-form {
  margin-top: 20px;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.login-button {
  height: 44px;
  font-size: 16px;
  font-weight: 500;
  margin-top: 8px;
}

.login-footer {
  margin-top: 24px;
  text-align: center;
}

.login-footer p {
  color: #909399;
  font-size: 13px;
  margin: 0;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  padding: 12px 16px;
}

:deep(.el-form-item__content) {
  width: 100%;
}

:deep(.el-alert) {
  margin-top: 16px;
  border-radius: 8px;
}
</style>
