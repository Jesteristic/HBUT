<template>
  <div class="login-container">
    <el-card class="login-card" shadow="hover">
      <template #header>
        <div class="login-header">
          <el-icon color="#409eff" size="48">
            <User/>
          </el-icon>
          <h2>专利分析系统</h2>
          <p>请登录您的账户</p>
        </div>
      </template>
      <LoginForm @login="handleLogin"/>
    </el-card>
  </div>
</template>
<script>
import LoginForm from './LoginForm.vue'
import axios from 'axios'
import {User} from '@element-plus/icons-vue'

export default {
  components: {LoginForm, User},
  methods: {
    async handleLogin(creds) {
      try {
        await axios.post('/api/login', creds)
        // redirect to dashboard after successful login
        this.$router.push('/dashboard')
      } catch (e) {
        this.$message.error('登录失败')
      }
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