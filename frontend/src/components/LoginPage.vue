<template>
  <div class="login-container">
    <el-card class="login-card" shadow="hover">
      <template #header>
        <div class="login-header">
          <el-icon color="#409eff" size="48">
            <User/>
          </el-icon>
          <h2>专利分析系统</h2>
          <p>{{ isLogin ? '请选择登录类型并登录' : '请注册新账户' }}</p>
        </div>
      </template>
      <div class="login-type-switch">
        <el-radio-group v-model="loginType" size="large">
          <el-radio-button value="user">用户登录</el-radio-button>
          <el-radio-button value="admin">管理员登录</el-radio-button>
        </el-radio-group>
      </div>
      <LoginForm v-if="isLogin" ref="loginForm" @login="handleLogin"/>
      <RegisterForm v-if="!isLogin && loginType === 'user'" @register="handleRegister"/>
      <div style="text-align: center; margin-top: 20px;">
        <el-button type="link" @click="isLogin = !isLogin">
          {{ isLogin ? '没有账户？点击注册' : '已有账户？点击登录' }}
        </el-button>
      </div>
    </el-card>
  </div>
</template>
<script>
import LoginForm from './LoginForm.vue'
import RegisterForm from './RegisterForm.vue'
import axios from 'axios'
import {User} from '@element-plus/icons-vue'
import {inject} from 'vue'

export default {
  components: {LoginForm, RegisterForm, User},
  data() {
    return {
      isLogin: true,
      loginType: 'user'
    }
  },
  setup() {
    const authStore = inject('authStore')
    return {
      authStore
    }
  },
  methods: {
    async handleLogin(creds, retryCount = 0) {
      const maxRetries = 3
      const retryDelay = 1000 * (retryCount + 1) // 递增延迟

      try {
        console.log(`发送登录请求 (尝试 ${retryCount + 1}/${maxRetries + 1}):`, {...creds, loginType: this.loginType})

        // 显示加载状态
        const loading = this.$loading({
          lock: true,
          text: '正在登录...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        })

        // 使用authStore的login方法，确保状态同步
        const response = await this.authStore.login({...creds, loginType: this.loginType})

        loading.close()
        console.log('登录响应:', response)

        if (response.ok) {
          console.log('登录成功，开始跳转...')
          this.$message.success('登录成功！')

          // 登录成功，保存凭据到localStorage用于自动填充
          if (creds.remember) {
            localStorage.setItem('savedUsername', creds.username)
            localStorage.setItem('savedPassword', creds.password)
            localStorage.setItem('loginType', this.loginType)
          }

          console.log('authStore状态已更新，准备跳转')
          console.log('当前authStore状态:', {
            isAuthenticated: this.authStore.isAuthenticated,
            loginType: this.authStore.loginType,
            lastCheck: this.authStore.lastCheck
          })

          // 立即跳转，因为authStore状态已经同步更新
          if (this.loginType === 'admin') {
            console.log('跳转到管理员页面')
            this.$router.push('/admin')
          } else {
            console.log('跳转到专利页面')
            this.$router.push('/patents')
          }

        } else {
          loading.close()
          console.log('登录失败:', response)
          const errorMsg = response.error || '登录失败'
          this.$message.error(errorMsg)

          // 如果是服务器错误且未达到最大重试次数，自动重试
          if (response.status >= 500 && retryCount < maxRetries) {
            console.log(`服务器错误，${retryDelay}ms后重试...`)
            this.$message.warning(`连接服务器失败，${retryDelay / 1000}秒后自动重试...`)
            setTimeout(() => {
              this.handleLogin(creds, retryCount + 1)
            }, retryDelay)
          }
        }
      } catch (e) {
        // 隐藏加载状态
        this.$loading?.close?.()

        console.error('登录错误:', e)
        const errorMsg = e.response?.data?.error || e.message || '网络错误'

        // 处理不同类型的错误
        if (e.code === 'NETWORK_ERROR' || !navigator.onLine) {
          this.$message.error('网络连接失败，请检查网络连接')
        } else if (e.response?.status === 429) {
          this.$message.error('请求过于频繁，请稍后再试')
        } else if (e.response?.status >= 500) {
          // 服务器错误，自动重试
          if (retryCount < maxRetries) {
            console.log(`服务器错误，${retryDelay}ms后重试...`)
            this.$message.warning(`服务器错误，${retryDelay / 1000}秒后自动重试...`)
            setTimeout(() => {
              this.handleLogin(creds, retryCount + 1)
            }, retryDelay)
            return
          } else {
            this.$message.error('服务器暂时不可用，请稍后重试')
          }
        } else {
          this.$message.error(`登录失败: ${errorMsg}`)
        }
      }
    },
    async handleRegister(creds) {
      try {
        const response = await axios.post('/api/register', creds)
        this.$message.success(response.data.message)
        this.isLogin = true  // 注册成功后切换到登录
      } catch (e) {
        this.$message.error(e.response?.data?.error || '注册失败')
      }
    }
  },
  mounted() {
    // 自动填充记住的凭据
    const savedUsername = localStorage.getItem('savedUsername')
    const savedPassword = localStorage.getItem('savedPassword')
    const savedLoginType = localStorage.getItem('loginType')

    this.$nextTick(() => {
      const loginForm = this.$refs.loginForm
      if (loginForm && savedUsername && savedPassword) {
        loginForm.form.username = savedUsername
        loginForm.form.password = savedPassword
        loginForm.form.remember = true
      }
    })

    if (savedLoginType) {
      this.loginType = savedLoginType
    }
  }
}
</script>
<style scoped>
.login-container {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.login-header {
  text-align: center;
  color: #303133;
}

.login-header h2 {
  margin: 10px 0;
  color: #409eff;
  font-weight: 600;
}

.login-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}
</style>