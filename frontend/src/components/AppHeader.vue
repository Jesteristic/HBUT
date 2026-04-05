<template>
  <el-header class="app-header">
    <div class="header-content">
      <div class="logo-section">
        <el-icon color="#fff" size="32">
          <DocumentAdd/>
        </el-icon>
        <h1>专利分析系统</h1>
      </div>
      <el-menu :default-active="$route.path" active-text-color="#ffd04b" background-color="transparent" class="nav-menu"
               mode="horizontal" text-color="#fff">
        <el-menu-item index="/dashboard">
          <el-icon>
            <Monitor/>
          </el-icon>
          <span>控制台</span>
        </el-menu-item>
        <el-menu-item index="/patents">
          <el-icon>
            <Document/>
          </el-icon>
          <span>专利管理</span>
        </el-menu-item>
        <el-menu-item index="/analysis">
          <el-icon>
            <DataAnalysis/>
          </el-icon>
          <span>技术分析</span>
        </el-menu-item>
      </el-menu>
      <div class="user-section">
        <el-avatar :size="32" :src="user.avatar" icon="User"/>
        <span class="username">{{ user.username }}</span>
        <el-button class="logout-btn" type="text" @click="logout">
          <el-icon>
            <SwitchButton/>
          </el-icon>
          退出
        </el-button>
      </div>
    </div>
  </el-header>
</template>

<script>
import axios from 'axios'
import {DataAnalysis, Document, DocumentAdd, Monitor, SwitchButton, User} from '@element-plus/icons-vue'

export default {
  name: 'AppHeader',
  components: {DocumentAdd, Monitor, Document, DataAnalysis, User, SwitchButton},
  data() {
    return {
      user: {}
    }
  },
  mounted() {
    this.getUser()
  },
  methods: {
    getUser() {
      axios.get('/api/status').then(r => {
        this.user = r.data.user || {}
      })
    },
    logout() {
      axios.get('/api/logout').then(() => {
        this.$router.push('/login')
      })
    }
  }
}
</script>

<style scoped>
.app-header {
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-section h1 {
  margin: 0;
  color: #fff;
  font-size: 24px;
  font-weight: 600;
}

.nav-menu {
  border-bottom: none !important;
  background: transparent !important;
}

.nav-menu .el-menu-item {
  border-bottom: none !important;
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #fff;
}

.username {
  font-weight: 500;
}

.logout-btn {
  color: #fff !important;
  display: flex;
  align-items: center;
  gap: 5px;
}
</style>