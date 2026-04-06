<template>
  <el-card class="tasks-card" shadow="hover">
    <h2>任务列表</h2>
    <el-table :data="tasks" border stripe style="width: 100%">
      <el-table-column label="序号" prop="id" sortable width="60"></el-table-column>
      <el-table-column label="关键字" min-width="150" prop="keyword" sortable></el-table-column>
      <el-table-column label="页大小" prop="page_size" sortable width="100"></el-table-column>
      <el-table-column label="页数" prop="pages" sortable width="80"></el-table-column>
      <el-table-column label="队列" prop="queue_order" width="80"></el-table-column>
      <el-table-column :formatter="formatStatus" label="状态" prop="status" width="140"></el-table-column>
      <el-table-column :formatter="formatDate" label="创建时间" prop="created_at" width="200"></el-table-column>
      <el-table-column fixed="right" label="操作" width="180">
        <template #default="{ row }">
          <el-button size="mini" type="text" @click="$emit('delete', row.id)">删除</el-button>
          <el-dropdown size="mini" trigger="click">
            <span class="el-dropdown-link">更多<i class="el-icon-arrow-down el-icon--right"></i></span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-if="row.status === 'pending'" @click="$emit('move', row.id, 'up')">上移
                </el-dropdown-item>
                <el-dropdown-item v-if="row.status === 'pending'" @click="$emit('move', row.id, 'down')">下移
                </el-dropdown-item>
                <el-dropdown-item v-if="row.status === 'running'" @click="$emit('cancel', row.id)">取消
                </el-dropdown-item>
                <el-dropdown-item @click="$emit('rerun', row.id)">重跑</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </el-table-column>
    </el-table>
    <div style="text-align:right; margin-top:10px;">
      <el-pagination
          :current-page.sync="page"
          :page-size="per"
          :total="total"
          background
          layout="prev, pager, next"
          @current-change="fetch"
      ></el-pagination>
    </div>
  </el-card>
</template>
<script>
export default {
  props: ['tasks', 'total', 'page', 'per'],
  emits: ['page-change', 'delete', 'rerun', 'move', 'cancel'],
  methods: {
    formatStatus(row, column, cellValue) {
      const status = cellValue || (row && row.status);
      const map = {
        pending: '排队中',
        running: '采集中',
        done: '采集完成',
        completed: '已完成',
        failed: '失败',
        canceled: '已取消'
      };
      return map[status] || status || '';
    },
    formatDate(row, column, cellValue) {
      let dateStr = cellValue || (row && row.created_at);
      if (!dateStr) return '';
      if (typeof dateStr === 'string') {
        dateStr = dateStr.trim();
        if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/.test(dateStr)) {
          // 避免浏览器将无时区 ISO 字符串当 UTC 解析
          dateStr = dateStr.replace('T', ' ');
        }
      }
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return '';
      return date.getFullYear() + '-' +
          (date.getMonth() + 1).toString().padStart(2, '0') + '-' +
          date.getDate().toString().padStart(2, '0') + ' ' +
          (date.getHours() - 8).toString().padStart(2, '0') + ':' +
          date.getMinutes().toString().padStart(2, '0') + ':' +
          date.getSeconds().toString().padStart(2, '0');
    },
    fetch(page) {
      this.$emit('page-change', page);
    }
  }
}
</script>
<style scoped>
.tasks-card {
  margin: 20px;
}
</style>