<template>
  <div class="app-layout">
    <!-- 顶部主导航 -->
    <el-header class="app-header">
      <div class="header-content">
        <div class="header-left">
          <el-button class="menu-toggle" type="text" @click="toggleSidebar">
            <el-icon>
              <Fold v-if="!sidebarCollapsed"/>
              <Expand v-else/>
            </el-icon>
          </el-button>
          <div class="logo-section">
            <el-icon color="#fff" size="32">
              <DocumentAdd/>
            </el-icon>
            <h1>专利分析系统</h1>
          </div>
        </div>
        <div class="user-section">
          <el-badge :value="notificationCount" class="notification-badge">
            <el-button type="text" @click="showNotifications">
              <el-icon size="20">
                <Bell/>
              </el-icon>
            </el-button>
          </el-badge>
          <el-avatar :size="32" :src="user.avatar" icon="User"/>
          <span class="username">{{ user.username }}</span>
          <el-button class="logout-btn" type="link" @click="logout">
            <el-icon>
              <SwitchButton/>
            </el-icon>
            退出
          </el-button>
        </div>
      </div>
    </el-header>

    <el-container class="main-container">
      <!-- 左侧子导航 -->
      <el-aside :width="sidebarCollapsed ? '64px' : '200px'" class="app-sidebar">
        <el-menu
            :collapse="sidebarCollapsed"
            :default-active="$route.path"
            active-text-color="#409eff"
            background-color="#304156"
            class="sidebar-menu"
            text-color="#bfcbd9"
            @select="onMenuSelect"
        >
          <el-menu-item index="/patents">
            <el-icon>
              <Document/>
            </el-icon>
            <template #title>专利管理</template>
          </el-menu-item>
          <el-menu-item v-if="!isAdmin" index="/analysis">
            <el-icon>
              <DataAnalysis/>
            </el-icon>
            <template #title>技术分析</template>
          </el-menu-item>
          <el-menu-item v-if="isAdmin" index="/admin">
            <el-icon>
              <Monitor/>
            </el-icon>
            <template #title>管理控制台</template>
          </el-menu-item>
          <el-menu-item v-if="isAdmin" index="/users">
            <el-icon>
              <User/>
            </el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区域 -->
      <el-main class="app-main">
        <router-view/>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import axios from 'axios'
import {
  Bell,
  DataAnalysis,
  Document,
  DocumentAdd,
  Expand,
  Fold,
  Monitor,
  SwitchButton,
  User
} from '@element-plus/icons-vue'

export default {
  name: 'AppLayout',
  components: {DocumentAdd, Monitor, Document, DataAnalysis, User, SwitchButton, Bell, Fold, Expand},
  data() {
    return {
      user: {},
      loginMode: 'user',
      notificationCount: 0,
      notifications: [],
      sidebarCollapsed: false
    }
  },
  computed: {
    isAdmin() {
      return this.loginMode === 'admin'
    }
  },
  mounted() {
    this.getUser()
  },
  methods: {
    getUser() {
      axios.get('/api/status').then(r => {
        this.user = r.data.user || {}
        this.loginMode = r.data.login_type || 'user'
      })
    },
    logout() {
      axios.get('/api/logout').then(() => {
        this.$router.push('/login')
      })
    },
    onMenuSelect(path) {
      this.$router.push(path)
    },
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },
    showNotifications() {
      this.$message.info('通知功能开发中...')
    }
  }
}
</script>

<style scoped>
.app-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 1000;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  height: 100%;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.menu-toggle {
  color: #fff;
  margin-right: 10px;
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

.notification-badge {
  margin-right: 10px;
}

.main-container {
  flex: 1;
  display: flex;
}

.app-sidebar {
  background-color: #304156;
  border-right: 1px solid #e6e6e6;
}

.sidebar-menu {
  border-right: none;
  height: 100%;
}

.sidebar-menu .el-menu-item {
  height: 48px;
  line-height: 48px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.app-main {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}
</style>