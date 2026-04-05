<template>
  <el-card class="tasks-card" shadow="hover">
    <h2>任务历史</h2>
    <el-table :data="tasks" style="width: 100%">
      <el-table-column label="#" prop="id" width="60"></el-table-column>
      <el-table-column label="关键字" prop="keyword"></el-table-column>
      <el-table-column label="页大小" prop="page_size" width="100"></el-table-column>
      <el-table-column label="页数" prop="pages" width="80"></el-table-column>
      <el-table-column label="状态" prop="status" width="100"></el-table-column>
      <el-table-column label="创建时间" prop="created_at" width="180"></el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="mini" type="danger" @click="$emit('delete', row.id)">删除</el-button>
          <el-button size="mini" type="primary" @click="$emit('rerun', row.id)">重跑</el-button>
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
}
</script>