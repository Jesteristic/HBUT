<template>
  <el-card class="login-card" shadow="hover" style="max-width:350px; margin:auto;">
    <el-form :model="form" label-width="80px" @submit.prevent="submit">
      <el-form-item label="用户名">
        <el-input v-model="form.username"></el-input>
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" type="password"></el-input>
      </el-form-item>
      <el-form-item>
        <el-checkbox v-model="form.remember">记住我</el-checkbox>
      </el-form-item>
      <el-form-item style="text-align:right;">
        <el-button type="primary" @click="submit">登录</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>
<script>
export default {
  data() {
    return {
      form: {username: '', password: '', remember: false}
    }
  },
  methods: {
    submit() {
      this.$emit('login', {...this.form})
    }
  }
}
</script>