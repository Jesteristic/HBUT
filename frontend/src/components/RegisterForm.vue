<template>
  <el-card class="register-card" shadow="hover" style="max-width:350px; margin:auto;">
    <el-form :model="form" label-width="80px" @submit.prevent="submit">
      <el-form-item label="用户名">
        <el-input v-model="form.username"></el-input>
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" type="password"></el-input>
      </el-form-item>
      <el-form-item label="确认密码">
        <el-input v-model="form.confirmPassword" type="password"></el-input>
      </el-form-item>
      <el-form-item style="text-align:right;">
        <el-button type="primary" @click="submit">注册</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>
<script>
export default {
  data() {
    return {
      form: {username: '', password: '', confirmPassword: ''}
    }
  },
  methods: {
    submit() {
      if (this.form.password !== this.form.confirmPassword) {
        this.$message.error('密码不匹配')
        return
      }
      this.$emit('register', {username: this.form.username, password: this.form.password})
    }
  }
}
</script>