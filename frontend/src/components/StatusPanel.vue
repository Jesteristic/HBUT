<template>
  <div>
    <h2>队列 & 线程状态</h2>
    <el-row :gutter="20">
      <el-col :span="6">待处理搜索任务：{{status.producer_tasks}}</el-col>
      <el-col :span="6">taskId 队列长度：{{status.task_queue}}</el-col>
      <el-col :span="6">生产者线程：{{status.producers_running}}</el-col>
      <el-col :span="6">消费者线程：{{status.consumers_running}}</el-col>
    </el-row>
    <el-button type="primary" @click="$emit('refresh')">刷新状态</el-button>
    <el-button type="success" @click="doStart">启动爬虫</el-button>
    <el-button type="warning" @click="$emit('stop')">停止爬虫</el-button>
  </div>
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