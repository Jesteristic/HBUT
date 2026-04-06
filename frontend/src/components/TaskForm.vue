<template>
  <el-card class="task-form-card" shadow="hover" style="margin-bottom:20px;">
    <el-form :model="task" label-width="80px" @submit.native.prevent="submit">
      <el-form-item label="关键词">
        <el-input v-model="task.keyword" placeholder="请输入搜索词，或使用下方批量关键词"></el-input>
      </el-form-item>
      <el-form-item label="批量关键词">
        <el-input v-model="task.batch_keywords" placeholder="每行一个关键词，可留空使用单条关键词" rows="4"
                  type="textarea"></el-input>
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
  </el-card>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return {
      task: {
        keyword: '',
        batch_keywords: '',
        page_size: 20,
        pages: 1
      }
    }
  },
  methods: {
    submit() {
      const keys = this.task.batch_keywords
          .split('\n')
          .map(line => line.trim())
          .filter(Boolean)

      if (keys.length > 0) {
        const tasks = keys.map(keyword => ({
          keyword,
          page_size: this.task.page_size,
          pages: this.task.pages
        }))
        axios.post('/api/tasks/batch', {tasks}).then(() => {
          this.reset()
          this.$emit('submitted')
          this.$message.success('已批量提交任务')
        }).catch(() => {
          this.$message.error('批量提交失败')
        })
        return
      }

      if (!this.task.keyword.trim()) {
        this.$message.warning('请输入关键词或批量关键词')
        return
      }

      axios.post('/api/task', {
        keyword: this.task.keyword.trim(),
        page_size: this.task.page_size,
        pages: this.task.pages
      }).then(() => {
        this.reset()
        this.$emit('submitted')
        this.$message.success('已提交任务')
      }).catch(() => {
        this.$message.error('提交任务失败')
      })
    },
    reset() {
      this.task.keyword = ''
      this.task.batch_keywords = ''
      this.task.page_size = 20
      this.task.pages = 1
    }
  }
}
</script>