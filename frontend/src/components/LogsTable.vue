<template>
  <div>
    <h2>日志</h2>
    <el-table :data="logs" style="width: 100%">
      <el-table-column prop="created_at" label="时间" width="180"></el-table-column>
      <el-table-column prop="action" label="动作" width="120"></el-table-column>
      <el-table-column prop="keyword" label="关键字"></el-table-column>
      <el-table-column prop="page" label="页" width="60"></el-table-column>
      <el-table-column prop="status" label="状态" width="100"></el-table-column>
      <el-table-column prop="details" label="详情"></el-table-column>
    </el-table>
  </div>
</template>
<script>
export default {
  props: ['logs']
}
</script>