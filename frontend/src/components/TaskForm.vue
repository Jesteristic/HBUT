<template>
  <el-form :model="task" @submit.native.prevent="submit" label-width="60px" inline>
    <el-form-item label="关键词">
      <el-input v-model="task.keyword" required></el-input>
    </el-form-item>
    <el-form-item label="页大小">
      <el-input-number v-model="task.page_size" :min="1"></el-input-number>
    </el-form-item>
    <el-form-item label="页数">
      <el-input-number v-model="task.pages" :min="1"></el-input-number>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="submit">提交任务</el-button>
    </el-form-item>
  </el-form>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return { task: { keyword: '', page_size: 20, pages: 1 } }
  },
  methods: {
    submit() {
      axios.post('/api/task', this.task).then(() => {
        this.$emit('submitted')
        alert('已提交任务')
      })
    }
  }
}
</script>