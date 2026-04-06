<template>
  <div class="status-panel">
    <!-- 状态指标部分 -->
    <el-card :body-style="{ padding: '20px' }" class="status-card" shadow="hover">
      <div class="status-metrics">
        <div v-for="metric in metrics" :key="metric.key" :style="{ '--metric-color': metric.color }"
             class="metric-item">
          <div class="metric-header">
            <div class="metric-icon">
              <el-icon :size="20">
                <component :is="metric.icon"/>
              </el-icon>
            </div>
            <span class="metric-label">{{ metric.label }}</span>
          </div>
          <div class="metric-value">{{ formatValue(status[metric.key]) }}</div>
          <div class="metric-footer">
            <span class="metric-desc">{{ metric.desc }}</span>
            <el-tag v-if="metric.showTrend" :type="getTrendType(status[metric.key])" effect="light" size="small">
              {{ getTrendText(status[metric.key]) }}
            </el-tag>
          </div>
        </div>
      </div>

      <!-- 操作按钮部分 -->
      <el-divider class="divider"/>
      <div class="action-buttons">
        <el-button
            :icon="Refresh"
            :loading="refreshing"
            type="primary"
            @click="$emit('refresh')"
        >
          刷新状态
        </el-button>

        <el-button
            :class="{ 'active': autoRefresh }"
            :icon="Timer"
            type="info"
            @click="toggleAutoRefresh"
        >
          {{ autoRefresh ? '停止自动刷新' : '启动自动刷新' }}
        </el-button>

        <el-popover
            :width="300"
            placement="bottom"
            title="启动爬虫配置"
            trigger="click"
        >
          <template #reference>
            <el-button :icon="VideoPlay" type="success">开始采集</el-button>
          </template>
          <div class="config-form">
            <div class="config-item">
              <label>生产者数量</label>
              <el-input-number
                  v-model="config.producers"
                  :max="10"
                  :min="1"
                  controls-position="right"
                  size="small"
              />
            </div>
            <div class="config-item">
              <label>消费者数量</label>
              <el-input-number
                  v-model="config.consumers"
                  :max="20"
                  :min="1"
                  controls-position="right"
                  size="small"
              />
            </div>
            <div class="config-actions">
              <el-button size="small" type="primary" @click="handleStart">确认启动</el-button>
              <el-button size="small" @click="resetConfig">重置</el-button>
            </div>
          </div>
        </el-popover>

        <el-popconfirm
            cancel-button-text="取消"
            confirm-button-text="确定"
            title="确定要停止采集吗？"
            @confirm="$emit('stop')"
        >
          <template #reference>
            <el-button :icon="VideoPause" type="warning">停止采集</el-button>
          </template>
        </el-popconfirm>

        <el-tooltip content="查看详细日志" placement="top">
          <el-button :icon="Document" circle type="info" @click="$emit('view-logs')"/>
        </el-tooltip>

        <el-tooltip content="系统设置" placement="top">
          <el-button :icon="Setting" circle type="info" @click="$emit('settings')"/>
        </el-tooltip>
      </div>

      <!-- 状态指示器 -->
      <div class="status-indicator">
        <span class="indicator-label">系统状态:</span>
        <span :class="getSystemStatusClass" class="indicator-dot"></span>
        <span class="indicator-text">{{ getSystemStatusText }}</span>
      </div>
    </el-card>

    <!-- 系统统计信息 -->
    <el-card :body-style="{ padding: '20px' }" class="stats-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon>
            <TrendCharts/>
          </el-icon>
          <span>系统统计</span>
          <el-tag size="small" type="info">{{ formatTime(new Date()) }}</el-tag>
        </div>
      </template>

      <div class="system-stats">
        <div class="stat-row">
          <div class="stat-item">
            <span class="stat-label">成功率</span>
            <span class="stat-value success">{{ status.system_stats?.success_rate || 0 }}%</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">内存使用</span>
            <span :class="getMemoryClass(status.system_stats?.memory_usage || 0)" class="stat-value">
              {{ status.system_stats?.memory_usage || 0 }}%
            </span>
          </div>
          <div class="stat-item">
            <span class="stat-label">CPU使用</span>
            <span :class="getCpuClass(status.system_stats?.cpu_usage || 0)" class="stat-value">
              {{ status.system_stats?.cpu_usage || 0 }}%
            </span>
          </div>
        </div>

        <div class="stat-row">
          <div class="stat-item">
            <span class="stat-label">最近成功</span>
            <span class="stat-value success">{{ status.system_stats?.recent_success || 0 }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">最近错误</span>
            <span class="stat-value error">{{ status.system_stats?.recent_errors || 0 }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">错误率</span>
            <span :class="getErrorClass(status.performance_metrics?.error_rate || 0)" class="stat-value">
              {{ status.performance_metrics?.error_rate || 0 }}%
            </span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 队列详情 -->
    <el-card :body-style="{ padding: '20px' }" class="queue-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon>
            <List/>
          </el-icon>
          <span>队列详情</span>
        </div>
      </template>

      <div class="queue-details">
        <div class="queue-section">
          <h4>最近生产任务 ({{ status.queue_details?.recent_producer_tasks?.length || 0 }})</h4>
          <div class="task-list">
            <div v-if="status.queue_details?.recent_producer_tasks?.length === 0" class="empty-state">
              队列为空
            </div>
            <div v-for="(task, index) in status.queue_details.recent_producer_tasks" v-else :key="index"
                 class="task-item">
              <span class="task-index">{{ index + 1 }}</span>
              <span class="task-content">{{ task }}</span>
            </div>
          </div>
        </div>

        <div class="queue-section">
          <h4>最近任务ID ({{ status.queue_details?.recent_task_ids?.length || 0 }})</h4>
          <div class="task-list">
            <div v-if="status.queue_details?.recent_task_ids?.length === 0" class="empty-state">
              队列为空
            </div>
            <div v-for="(taskId, index) in status.queue_details.recent_task_ids" v-else :key="index" class="task-item">
              <span class="task-index">{{ index + 1 }}</span>
              <span class="task-content">{{ taskId }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import {ref, computed, reactive, onMounted, onUnmounted, markRaw} from 'vue'
import {
  Refresh,
  VideoPlay,
  VideoPause,
  Document,
  Setting,
  Clock,
  List,
  User,
  Timer,
  TrendCharts
} from '@element-plus/icons-vue'

const props = defineProps({
  status: {
    type: Object,
    default: () => ({
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
    })
  },
  refreshing: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['refresh', 'start', 'stop', 'view-logs', 'settings'])

// 配置信息
const config = reactive({
  producers: 1,
  consumers: 1
})

// 自动刷新状态
const autoRefresh = ref(false)
const refreshInterval = ref(null)
const refreshIntervalTime = 5000 // 5秒自动刷新

// 指标定义
const metrics = ref([
  {
    key: 'producer_tasks',
    label: '待处理任务',
    desc: '等待处理的搜索任务',
    icon: markRaw(Clock),
    color: '#409EFF',
    showTrend: true
  },
  {
    key: 'task_queue',
    label: '任务队列',
    desc: 'TaskId 队列长度',
    icon: markRaw(List),
    color: '#E6A23C',
    showTrend: true
  },
  {
    key: 'producers_running',
    label: '生产者',
    desc: '活跃生产者线程',
    icon: markRaw(User),
    color: '#67C23A'
  },
  {
    key: 'consumers_running',
    label: '消费者',
    desc: '活跃消费者线程',
    icon: markRaw(User),
    color: '#F56C6C'
  }
])

// 格式化数值显示
const formatValue = (value) => {
  if (value >= 10000) return (value / 10000).toFixed(1) + 'w'
  if (value >= 1000) return (value / 1000).toFixed(1) + 'k'
  return value
}

// 格式化时间
const formatTime = (date) => {
  return date.toLocaleTimeString('zh-CN', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 趋势类型
const getTrendType = (value) => {
  if (value === 0) return 'info'
  if (value < 10) return 'success'
  if (value < 50) return 'warning'
  return 'danger'
}

// 趋势文本
const getTrendText = (value) => {
  if (value === 0) return '空闲'
  if (value < 10) return '正常'
  if (value < 50) return '较高'
  return '繁忙'
}

// 系统状态类名
const getMemoryClass = (usage) => {
  if (usage < 50) return 'success'
  if (usage < 80) return 'warning'
  return 'error'
}

const getCpuClass = (usage) => {
  if (usage < 30) return 'success'
  if (usage < 70) return 'warning'
  return 'error'
}

const getErrorClass = (rate) => {
  if (rate < 5) return 'success'
  if (rate < 15) return 'warning'
  return 'error'
}

// 处理启动
const handleStart = () => {
  emit('start', {
    producers: config.producers,
    consumers: config.consumers
  })
}

// 重置配置
const resetConfig = () => {
  config.producers = 1
  config.consumers = 1
}

// 切换自动刷新
const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

// 开始自动刷新
const startAutoRefresh = () => {
  if (refreshInterval.value) return
  refreshInterval.value = setInterval(() => {
    emit('refresh')
  }, refreshIntervalTime)
}

// 停止自动刷新
const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

// 计算系统状态
const getSystemStatusClass = computed(() => {
  const {producer_tasks, producers_running, consumers_running} = props.status

  if (producers_running === 0 && consumers_running === 0) return 'stopped'
  if (producer_tasks === 0 && producers_running > 0) return 'idle'
  if (producer_tasks > 0 && producers_running > 0 && consumers_running > 0) return 'running'
  return 'warning'
})

const getSystemStatusText = computed(() => {
  const {producer_tasks, producers_running, consumers_running} = props.status

  if (producers_running === 0 && consumers_running === 0) return '已停止'
  if (producer_tasks === 0 && producers_running > 0) return '空闲中'
  if (producer_tasks > 0 && producers_running > 0 && consumers_running > 0) return '运行中'
  return '配置异常'
})

// 生命周期钩子
onMounted(() => {
  // 组件挂载时可以选择默认开启自动刷新
  // toggleAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.status-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.status-card {
  position: relative;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.status-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.status-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 10px;
}

.metric-item {
  padding: 16px;
  background: linear-gradient(135deg, rgba(var(--metric-color), 0.05) 0%, rgba(var(--metric-color), 0.02) 100%);
  border-radius: 10px;
  border-left: 4px solid var(--metric-color);
  transition: all 0.3s ease;
}

.metric-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(var(--metric-color), 0.15);
}

.metric-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.metric-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(var(--metric-color), 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
}

.metric-icon :deep(svg) {
  color: var(--metric-color);
}

.metric-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--metric-color);
  margin-bottom: 8px;
  line-height: 1.2;
}

.metric-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-desc {
  font-size: 12px;
  color: #909399;
}

.divider {
  margin: 20px 0;
}

.action-buttons {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.action-buttons .el-button.active {
  background-color: #67C23A;
  border-color: #67C23A;
  color: white;
}

.config-form {
  padding: 10px 0;
}

.config-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
}

.config-item label {
  font-size: 14px;
  color: #606266;
  min-width: 80px;
}

.config-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.status-indicator {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.indicator-label {
  color: #909399;
}

.indicator-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.indicator-dot.stopped {
  background-color: #F56C6C;
}

.indicator-dot.idle {
  background-color: #E6A23C;
}

.indicator-dot.running {
  background-color: #67C23A;
}

.indicator-dot.warning {
  background-color: #F56C6C;
  animation: pulse 2s infinite;
}

.indicator-text {
  font-weight: 500;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}

/* 系统统计卡片样式 */
.stats-card {
  border-radius: 12px;
  transition: all 0.3s ease;
}

.stats-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header .el-icon {
  color: #409EFF;
}

.system-stats {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  gap: 20px;
}

.stat-item {
  flex: 1;
  text-align: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #6c757d;
  margin-bottom: 8px;
  font-weight: 500;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #495057;
}

.stat-value.success {
  color: #28a745;
}

.stat-value.warning {
  color: #ffc107;
}

.stat-value.error {
  color: #dc3545;
}

/* 队列详情卡片样式 */
.queue-card {
  border-radius: 12px;
  transition: all 0.3s ease;
}

.queue-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.queue-details {
  display: flex;
  gap: 40px;
}

.queue-section {
  flex: 1;
}

.queue-section h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background: #fafafa;
}

.task-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 13px;
}

.task-item:last-child {
  border-bottom: none;
}

.task-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #409EFF;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  margin-right: 12px;
  flex-shrink: 0;
}

.task-content {
  flex: 1;
  word-break: break-all;
  color: #606266;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: #909399;
  font-style: italic;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .status-metrics {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-row {
    flex-direction: column;
    gap: 10px;
  }

  .queue-details {
    flex-direction: column;
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .status-metrics {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    flex-direction: column;
    align-items: stretch;
  }

  .action-buttons .el-button {
    width: 100%;
  }

  .status-indicator {
    position: static;
    justify-content: center;
    margin-top: 20px;
  }
}
</style>

<style scoped>
@media (max-width: 768px) {
  .status-metrics {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    flex-direction: column;
    align-items: stretch;
  }

  .action-buttons .el-button {
    width: 100%;
    margin: 5px 0 !important;
  }

  .status-indicator {
    position: static;
    margin-top: 15px;
    justify-content: center;
  }
}
</style>

<!-- 定义颜色变量 -->
<style>
:root {
  --metric-color-1: 64, 158, 255; /* #409EFF */
  --metric-color-2: 230, 162, 60; /* #E6A23C */
  --metric-color-3: 103, 194, 58; /* #67C23A */
  --metric-color-4: 245, 108, 108; /* #F56C6C */
}

/* 为每个指标项设置具体的颜色变量 */
.metric-item:nth-child(1) {
  --metric-color: rgb(var(--metric-color-1));
}

.metric-item:nth-child(2) {
  --metric-color: rgb(var(--metric-color-2));
}

.metric-item:nth-child(3) {
  --metric-color: rgb(var(--metric-color-3));
}

.metric-item:nth-child(4) {
  --metric-color: rgb(var(--metric-color-4));
}
</style>