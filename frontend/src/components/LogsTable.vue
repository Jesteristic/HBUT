<template>
  <el-card shadow="hover" class="logs-card" style="margin-bottom:20px;">
    <h2>日志</h2>
    <el-form inline :model="filter" class="filter-form" @submit.prevent="apply" style="margin-bottom:10px;">
      <el-form-item label="关键字">
        <el-input v-model="filter.keyword" size="small"></el-input>
      </el-form-item>
      <el-form-item label="动作">
        <el-input v-model="filter.action" size="small"></el-input>
      </el-form-item>
      <el-form-item label="起始">
        <el-date-picker v-model="filter.start" type="datetime" size="small" placeholder="开始"></el-date-picker>
      </el-form-item>
      <el-form-item label="结束">
        <el-date-picker v-model="filter.end" type="datetime" size="small" placeholder="结束"></el-date-picker>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" size="small" @click="apply">筛选</el-button>
      </el-form-item>
    </el-form>
    <el-table :data="logs" style="width: 100%">
      <el-table-column prop="created_at" label="时间" width="180"></el-table-column>
      <el-table-column prop="action" label="动作" width="120"></el-table-column>
      <el-table-column prop="keyword" label="关键字"></el-table-column>
      <el-table-column prop="page" label="页" width="60"></el-table-column>
      <el-table-column prop="status" label="状态" width="100"></el-table-column>
      <el-table-column prop="details" label="详情"></el-table-column>
    </el-table>
    <div style="text-align:right; margin-top:10px;">
      <el-pagination
        background
        layout="prev, pager, next"
        :total="total"
        :page-size="per"
        :current-page.sync="page"
        @current-change="changePage"
      ></el-pagination>
    </div>
  </el-card>
</template>
<script>
export default {
  props: ['logs','total','page','per'],
  data() {
    return {
      filter: { keyword: '', action: '', start: '', end: '' }
    }
  },
  methods: {
    apply() {
      this.$emit('filter', { ...this.filter })
    },
    changePage(p) {
      this.$emit('page-change', p)
    }
  }
}
</script>