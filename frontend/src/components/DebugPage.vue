<template>
  <div class="debug-container">
    <h2>🔧 登录调试工具</h2>

    <div class="debug-section">
      <h3>1. 检查认证状态</h3>
      <button :loading="checking" @click="checkAuth">检查认证状态</button>
      <pre v-if="authStatus">{{ JSON.stringify(authStatus, null, 2) }}</pre>
    </div>

    <div class="debug-section">
      <h3>2. 测试登录</h3>
      <div class="login-form">
        <input v-model="username" placeholder="用户名"/>
        <input v-model="password" placeholder="密码" type="password"/>
        <select v-model="loginType">
          <option value="user">用户登录</option>
          <option value="admin">管理员登录</option>
        </select>
        <button :loading="loggingIn" @click="testLogin">测试登录</button>
      </div>
      <pre v-if="loginResult">{{ JSON.stringify(loginResult, null, 2) }}</pre>
    </div>

    <div class="debug-section">
      <h3>3. 测试路由跳转</h3>
      <button @click="testNavigation">测试跳转到 /admin</button>
      <button @click="testNavigationPatents">测试跳转到 /patents</button>
      <button @click="testLoginAndNavigate">测试登录并跳转</button>
    </div>

    <div class="debug-section">
      <h3>4. 检查Session状态</h3>
      <button @click="checkSession">检查Session</button>
      <pre v-if="sessionInfo">{{ JSON.stringify(sessionInfo, null, 2) }}</pre>
    </div>

    <div class="debug-section">
      <h3>5. 清除状态</h3>
      <button @click="clearAll">清除所有状态</button>
    </div>

    <div class="debug-section">
      <h3>6. 网络连接测试</h3>
      <button @click="testConnection">测试网络连接</button>
      <pre v-if="connectionTest">{{ JSON.stringify(connectionTest, null, 2) }}</pre>
    </div>

    <div class="debug-section">
      <h3>7. 性能监控</h3>
      <button @click="checkPerformance">检查性能</button>
      <pre v-if="performanceData">{{ JSON.stringify(performanceData, null, 2) }}</pre>
    </div>

    <div class="debug-section">
      <h3>8. 错误日志</h3>
      <button @click="showLogs">显示错误日志</button>
      <button @click="clearLogs">清除日志</button>
      <pre v-if="errorLogs.length">{{ errorLogs.join('\n') }}</pre>
    </div>

    <div class="debug-section">
      <h3>9. 自动监控</h3>
      <button v-if="!monitoring" @click="startMonitoring">开始监控</button>
      <button v-if="monitoring" @click="stopMonitoring">停止监控</button>
      <div v-if="monitoring" class="monitoring-status">
        <p>监控中... 每5秒检查一次认证状态</p>
        <pre v-if="monitorResults.length">{{ monitorResults.slice(-5).join('\n') }}</pre>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import {inject} from 'vue'

export default {
  name: 'DebugPage',
  data() {
    return {
      authStatus: null,
      loginResult: null,
      sessionInfo: null,
      connectionTest: null,
      performanceData: null,
      errorLogs: [],
      monitorResults: [],
      monitoring: false,
      monitorInterval: null,
      checking: false,
      loggingIn: false,
      username: 'admin',
      password: 'admin',
      loginType: 'admin'
    }
  },
  setup() {
    const authStore = inject('authStore')
    return {
      authStore
    }
  },
  methods: {
    async checkAuth() {
      this.checking = true
      try {
        const response = await axios.get('/api/check-auth')
        this.authStatus = {
          status: response.status,
          data: response.data,
          headers: response.headers
        }
      } catch (error) {
        this.authStatus = {
          error: error.message,
          response: error.response?.data,
          status: error.response?.status
        }
      }
      this.checking = false
    },

    async testLogin() {
      this.loggingIn = true
      try {
        const response = await axios.post('/api/login', {
          username: this.username,
          password: this.password,
          loginType: this.loginType
        })
        this.loginResult = {
          status: response.status,
          data: response.data,
          headers: response.headers
        }

        // 如果登录成功，重新检查认证状态
        if (response.data.ok) {
          setTimeout(() => this.checkAuth(), 500)
        }
      } catch (error) {
        this.loginResult = {
          error: error.message,
          response: error.response?.data,
          status: error.response?.status
        }
      }
      this.loggingIn = false
    },

    testNavigation() {
      this.$router.push('/admin')
    },

    testNavigationPatents() {
      this.$router.push('/patents')
    },

    async testLoginAndNavigate() {
      try {
        console.log('开始测试登录并跳转...')
        console.log('当前authStore状态:', {
          isAuthenticated: this.authStore.isAuthenticated,
          loginType: this.authStore.loginType,
          lastCheck: this.authStore.lastCheck
        })

        // 使用authStore登录
        const result = await this.authStore.login({
          username: this.username,
          password: this.password,
          loginType: this.loginType
        })

        console.log('登录结果:', result)
        console.log('登录后的authStore状态:', {
          isAuthenticated: this.authStore.isAuthenticated,
          loginType: this.authStore.loginType,
          lastCheck: this.authStore.lastCheck
        })

        if (result.ok) {
          this.log('登录成功，准备跳转...')
          // 手动触发路由跳转，模拟LoginPage的行为
          setTimeout(() => {
            console.log('执行跳转...')
            if (this.loginType === 'admin') {
              this.$router.push('/admin')
            } else {
              this.$router.push('/patents')
            }
          }, 200)
        } else {
          this.log(`登录失败: ${result.error}`)
        }
      } catch (error) {
        console.error('测试登录错误:', error)
        this.log(`登录错误: ${error.message}`)
      }
    },

    async checkSession() {
      try {
        const response = await axios.get('/api/status')
        this.sessionInfo = {
          status: response.status,
          data: response.data
        }
      } catch (error) {
        this.sessionInfo = {
          error: error.message,
          response: error.response?.data,
          status: error.response?.status
        }
      }
    },

    clearAll() {
      this.authStatus = null
      this.loginResult = null
      this.sessionInfo = null
      this.connectionTest = null
      this.performanceData = null
      this.monitorResults = []
      this.stopMonitoring()
      // 清除localStorage
      localStorage.clear()
      // 清除session (通过访问logout端点)
      axios.post('/api/logout').catch(() => {
      })
      this.log('所有状态已清除')
    },

    async testConnection() {
      const startTime = Date.now()
      try {
        const response = await axios.get('/api/check-auth', {timeout: 5000})
        const endTime = Date.now()
        this.connectionTest = {
          status: 'success',
          responseTime: `${endTime - startTime}ms`,
          statusCode: response.status,
          server: response.headers['server'] || 'unknown'
        }
      } catch (error) {
        const endTime = Date.now()
        this.connectionTest = {
          status: 'failed',
          responseTime: `${endTime - startTime}ms`,
          error: error.message,
          code: error.code
        }
      }
      this.log(`网络连接测试: ${this.connectionTest.status}`)
    },

    checkPerformance() {
      const perfData = {
        navigation: {},
        timing: {},
        memory: {}
      }

      if (performance.timing) {
        const timing = performance.timing
        perfData.timing = {
          domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
          loadComplete: timing.loadEventEnd - timing.navigationStart,
          firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 'N/A'
        }
      }

      if (performance.memory) {
        perfData.memory = {
          used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024) + 'MB',
          total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024) + 'MB',
          limit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024) + 'MB'
        }
      }

      perfData.navigation = {
        userAgent: navigator.userAgent,
        cookieEnabled: navigator.cookieEnabled,
        onLine: navigator.onLine
      }

      this.performanceData = perfData
      this.log('性能数据已更新')
    },

    showLogs() {
      // 显示最近的错误日志
      this.errorLogs = [
        ...this.errorLogs,
        `[${new Date().toLocaleTimeString()}] 显示错误日志`
      ]
    },

    clearLogs() {
      this.errorLogs = []
      this.log('错误日志已清除')
    },

    startMonitoring() {
      this.monitoring = true
      this.monitorResults = []
      this.log('开始自动监控认证状态')

      this.monitorInterval = setInterval(async () => {
        try {
          const startTime = Date.now()
          const response = await axios.get('/api/check-auth')
          const endTime = Date.now()

          const result = `[${new Date().toLocaleTimeString()}] 认证状态: ${response.data.authenticated ? '已认证' : '未认证'} (${endTime - startTime}ms)`
          this.monitorResults.push(result)

          // 保持最近50条记录
          if (this.monitorResults.length > 50) {
            this.monitorResults = this.monitorResults.slice(-50)
          }
        } catch (error) {
          const result = `[${new Date().toLocaleTimeString()}] 认证检查失败: ${error.message}`
          this.monitorResults.push(result)
          this.log(`监控错误: ${error.message}`)
        }
      }, 5000)
    },

    stopMonitoring() {
      if (this.monitorInterval) {
        clearInterval(this.monitorInterval)
        this.monitorInterval = null
      }
      this.monitoring = false
      this.log('停止自动监控')
    },

    log(message) {
      const logEntry = `[${new Date().toLocaleTimeString()}] ${message}`
      this.errorLogs.push(logEntry)

      // 保持最近20条日志
      if (this.errorLogs.length > 20) {
        this.errorLogs = this.errorLogs.slice(-20)
      }
    }
  },

  beforeUnmount() {
    this.stopMonitoring()
  }
}
</script>

<style scoped>
.debug-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
}

.debug-section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.debug-section h3 {
  margin-top: 0;
  color: #409eff;
}

.login-form {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.login-form input, .login-form select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.login-form button {
  padding: 8px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.login-form button:hover {
  background: #337ecc;
}

pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
}

.monitoring-status {
  margin-top: 10px;
  padding: 10px;
  background: #f0f9ff;
  border: 1px solid #b3e5fc;
  border-radius: 4px;
}

.monitoring-status p {
  margin: 0 0 10px 0;
  color: #1976d2;
  font-weight: bold;
}
</style>