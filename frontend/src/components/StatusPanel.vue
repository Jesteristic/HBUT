<template>
  <el-card shadow="hover" class="status-card" style="margin-bottom:20px;">
    <h2>队列 & 线程状态</h2>
    <el-row :gutter="20" class="status-row">
      <el-col :span="6">
        <el-statistic label="待处理搜索任务" :value="status.producer_tasks" />
      </el-col>
      <el-col :span="6">
        <el-statistic label="taskId 队列" :value="status.task_queue" />
      </el-col>
      <el-col :span="6">
        <el-statistic label="生产者线程" :value="status.producers_running" />
      </el-col>
      <el-col :span="6">
        <el-statistic label="消费者线程" :value="status.consumers_running" />
      </el-col>
    </el-row>
    <div style="margin-top:15px;">
      <el-button type="primary" @click="$emit('refresh')">刷新状态</el-button>
      <el-button type="success" @click="doStart">启动爬虫</el-button>
      <el-button type="warning" @click="$emit('stop')">停止爬虫</el-button>
    </div>
  </el-card>
</template>

<script>
export default {
  props: ['status'],
  methods: {
    doStart() {
      const prod = parseInt(prompt('生产者数量', '1'))
      const cons = parseInt(prompt('消费者数量', '1'))
      this.$emit('start', { producers: prod, consumers: cons })
    }
  }
}
</script>