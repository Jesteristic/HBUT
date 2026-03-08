<template>
  <el-container style="padding:20px;">
    <el-header><h1>爬虫控制台</h1></el-header>
    <el-main>
      <TaskForm @submitted="refreshStatus" />
      <StatusPanel :status="status" @refresh="refreshStatus" @start="startCrawlers" @stop="stopCrawlers" />
      <LogsTable :logs="logs" />
    </el-main>
  </el-container>
</template>

<script>
import axios from 'axios'
import TaskForm from './components/TaskForm.vue'
import StatusPanel from './components/StatusPanel.vue'
import LogsTable from './components/LogsTable.vue'

export default {
  components: { TaskForm, StatusPanel, LogsTable },
  data() {
    return {
      status: {},
      logs: []
    }
  },
  methods: {
    refreshStatus() {
      axios.get('/api/status').then(r => this.status = r.data)
      axios.get('/api/logs').then(r => this.logs = r.data)
    },
    startCrawlers(cfg) {
      axios.post('/api/start', cfg).then(() => this.refreshStatus())
    },
    stopCrawlers() {
      axios.post('/api/stop').then(() => this.refreshStatus())
    }
  },
  mounted() {
    this.refreshStatus()
  }
}
</script>

<style>
body { font-family: Arial, sans-serif; margin:20px; }
table { border-collapse: collapse; width: 100%; }
th, td { border:1px solid #ccc; padding:4px; }
</style>