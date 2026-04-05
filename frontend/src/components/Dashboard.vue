<template>
  <div class="dashboard-container">
    <el-container style="height:100vh;">
      <AppHeader/>
      <el-main class="dashboard-main">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-card class="main-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <el-icon>
                    <Setting/>
                  </el-icon>
                  <span>系统控制台</span>
                </div>
              </template>
              <el-tabs v-model="activeTab" type="border-card">
                <el-tab-pane label="实时监控" name="dashboard">
                  <TaskForm @submitted="refreshStatus"/>
                  <StatusPanel :status="status" @refresh="refreshStatus" @start="startCrawlers" @stop="stopCrawlers"/>
                </el-tab-pane>
                <el-tab-pane label="日志监控" name="logs">
                  <LogsTable :logs="logs" :page="logsPage" :per="logsPer" :total="logsTotal"
                             @filter="onLogFilter" @page-change="onLogPageChange"/>
                </el-tab-pane>
                <el-tab-pane label="任务历史" name="tasks">
                  <TasksTable :page="tasksPage" :per="tasksPer" :tasks="tasks" :total="tasksTotal"
                              @delete="deleteTask" @rerun="rerunTask"/>
                </el-tab-pane>
              </el-tabs>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import axios from 'axios'
import AppHeader from './AppHeader.vue'
import TaskForm from './TaskForm.vue'
import StatusPanel from './StatusPanel.vue'
import LogsTable from './LogsTable.vue'
import TasksTable from './TasksTable.vue'
import {Setting} from '@element-plus/icons-vue'

export default {
  components: {AppHeader, TaskForm, StatusPanel, LogsTable, TasksTable, Setting},
  data() {
    return {
      status: {},
      logs: [],
      logsTotal: 0,
      logsPage: 1,
      logsPer: 20,
      logFilter: {},
      tasks: [],
      tasksTotal: 0,
      tasksPage: 1,
      tasksPer: 20,
      activeTab: 'dashboard'
    }
  },
  data() {
    return {
      status: {},
      logs: [],
      logsTotal: 0,
      logsPage: 1,
      logsPer: 20,
      logFilter: {},
      tasks: [],
      tasksTotal: 0,
      tasksPage: 1,
      tasksPer: 20,
      activeTab: 'dashboard',
      user: {}
    }
  },
  methods: {
    refreshStatus() {
      axios.get('/api/status').then(r => {
        this.status = r.data
        this.user = r.data.user || {}
      })
      this.fetchLogs()
    },
    startCrawlers(cfg) {
      axios.post('/api/start', cfg).then(() => this.refreshStatus())
    },
    stopCrawlers() {
      axios.post('/api/stop').then(() => this.refreshStatus())
    },
    fetchLogs() {
      const params = {page: this.logsPage, per: this.logsPer}
      const f = {...this.logFilter}
      if (f.start && typeof f.start.toISOString === 'function') f.start = f.start.toISOString()
      if (f.end && typeof f.end.toISOString === 'function') f.end = f.end.toISOString()
      Object.assign(params, f)
      axios.get('/api/logs', {params}).then(r => {
        this.logs = r.data.rows
        this.logsTotal = r.data.total
      })
    },
    onLogFilter(f) {
      this.logFilter = f
      this.logsPage = 1
      this.fetchLogs()
    },
    onLogPageChange(p) {
      this.logsPage = p
      this.fetchLogs()
    },
    fetchTasks() {
      axios.get('/api/tasks', {params: {page: this.tasksPage, per: this.tasksPer}}).then(r => {
        this.tasks = r.data.rows
        this.tasksTotal = r.data.total
      })
    },
    deleteTask(id) {
      axios.post(`/api/tasks/${id}/delete`).then(() => this.fetchTasks())
    },
    rerunTask(id) {
      axios.post(`/api/tasks/${id}/rerun`).then(() => this.fetchTasks())
    }
  },
  watch: {
    activeTab(val) {
      if (val === 'tasks') this.fetchTasks()
    }
  },
  mounted() {
    this.refreshStatus()
  }
}
</script>

<style scoped>
.dashboard-container {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.dashboard-header {
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

.dashboard-main {
  background: #f5f7fa;
  padding: 20px;
}

.main-card {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}
</style>

<style scoped>
/* small adjustments */
</style>