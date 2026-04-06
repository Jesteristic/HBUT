<template>
  <div class="dashboard-container">
    <el-row :gutter="20" class="dashboard-row">
      <el-col :lg="24" :md="24" :sm="24" :xl="24" :xs="24">
        <el-card class="main-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon>
                <Setting/>
              </el-icon>
              <span>系统控制台</span>
            </div>
          </template>
          <el-tabs v-model="activeTab" class="dashboard-tabs" type="border-card">
            <el-tab-pane label="实时监控" name="dashboard">
              <div class="tab-content">
                <TaskForm @submitted="refreshStatus"/>
                <StatusPanel
                    :refreshing="refreshing"
                    :status="status"
                    @refresh="refreshStatus"
                    @settings="activeTab = 'config'"
                    @start="startCrawlers"
                    @stop="stopCrawlers"
                    @view-logs="activeTab = 'logs'"
                />
              </div>
            </el-tab-pane>
            <el-tab-pane label="日志监控" name="logs">
              <div class="tab-content">
                <LogsTable :isAdmin="isAdmin" :logs="logs" :page="logsPage" :per="logsPer" :total="logsTotal"
                           @delete="deleteLog" @filter="onLogFilter" @page-change="onLogPageChange"/>
              </div>
            </el-tab-pane>
            <el-tab-pane label="任务列表" name="tasks">
              <div class="tab-content">
                <TasksTable :page="tasksPage" :per="tasksPer" :tasks="tasks" :total="tasksTotal"
                            @cancel="cancelTask" @delete="deleteTask" @move="moveTask" @rerun="rerunTask"
                            @page-change="onTaskPageChange"/>
              </div>
            </el-tab-pane>
            <el-tab-pane v-if="isAdmin" label="系统配置" name="config">
              <div class="tab-content">
                <el-form :model="config" label-width="120px">
                  <el-form-item label="最大页数">
                    <el-input-number v-model="config.max_pages" :max="100" :min="1"></el-input-number>
                  </el-form-item>
                  <el-form-item label="每页大小">
                    <el-input-number v-model="config.page_size" :max="100" :min="1"></el-input-number>
                  </el-form-item>
                  <el-form-item label="超时时间(秒)">
                    <el-input-number v-model="config.timeout" :max="300" :min="1"></el-input-number>
                  </el-form-item>
                  <el-form-item label="重试次数">
                    <el-input-number v-model="config.retry_times" :max="10" :min="0"></el-input-number>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="updateConfig">保存配置</el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import axios from 'axios'
import TaskForm from './TaskForm.vue'
import StatusPanel from './StatusPanel.vue'
import LogsTable from './LogsTable.vue'
import TasksTable from './TasksTable.vue'
import {Setting} from '@element-plus/icons-vue'

export default {
  components: {TaskForm, StatusPanel, LogsTable, TasksTable, Setting},
  data() {
    return {
      status: {
        producer_tasks: 0,
        task_queue: 0,
        producers_running: 0,
        consumers_running: 0,
        system_stats: {
          success_rate: 0,
          memory_usage: 0,
          cpu_usage: 0,
          recent_success: 0,
          recent_errors: 0
        },
        queue_details: {
          recent_producer_tasks: [],
          recent_task_ids: []
        },
        performance_metrics: {
          error_rate: 0
        }
      },
      refreshing: false,
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
      user: {},
      isAdmin: false,
      config: {
        max_pages: 1,
        page_size: 20,
        timeout: 30,
        retry_times: 3
      }
    }
  },
  methods: {
    refreshStatus() {
      this.refreshing = true
      axios.get('/api/status').then(r => {
        this.status = r.data
        this.user = r.data.user || {}
        this.isAdmin = r.data.login_type === 'admin'
        if (this.isAdmin) {
          this.fetchConfig()
        }
        console.log('Status updated:', this.status)
      }).catch(error => {
        console.error('Error refreshing status:', error)
        this.$message.error('获取状态失败')
      }).finally(() => {
        this.refreshing = false
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
    deleteLog(logId) {
      this.$confirm('确定删除这条日志吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        axios.post(`/api/logs/${logId}/delete`).then(() => {
          this.$message.success('删除成功')
          this.fetchLogs()
        }).catch(error => {
          this.$message.error('删除失败')
          console.error('Error deleting log:', error)
        })
      })
    },
    fetchConfig() {
      axios.get('/api/config').then(r => {
        this.config = r.data
      }).catch(error => {
        console.error('Error fetching config:', error)
      })
    },
    updateConfig() {
      axios.post('/api/config', this.config).then(() => {
        this.$message.success('配置更新成功')
      }).catch(error => {
        this.$message.error('配置更新失败')
        console.error('Error updating config:', error)
      })
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
    },
    moveTask(id, direction) {
      axios.post(`/api/tasks/${id}/move`, {direction}).then(() => this.fetchTasks())
    },
    cancelTask(id) {
      axios.post(`/api/tasks/${id}/cancel`).then(() => this.fetchTasks())
    },
    onTaskPageChange(page) {
      this.tasksPage = page
      this.fetchTasks()
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
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.dashboard-row {
  max-width: 1400px;
  margin: 0 auto;
}

.main-card {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: #409eff;
}

.dashboard-tabs {
  border-radius: 0 0 12px 12px;
}

.tab-content {
  padding: 20px 0;
  min-height: 400px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 10px;
  }

  .tab-content {
    padding: 10px 0;
  }
}
</style>