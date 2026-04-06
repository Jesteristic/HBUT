<template>
  <div class="page-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="main-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon>
                <User/>
              </el-icon>
              <span>用户管理</span>
            </div>
          </template>
          <el-table :data="users" stripe style="width: 100%">
            <el-table-column label="ID" prop="id" width="80"/>
            <el-table-column label="用户名" prop="username"/>
            <el-table-column label="角色" prop="role" width="120"/>
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button size="mini" type="danger" @click="deleteUser(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import axios from 'axios'
import {User} from '@element-plus/icons-vue'

export default {
  components: {User},
  data() {
    return {
      users: []
    }
  },
  mounted() {
    this.fetchUsers()
  },
  methods: {
    fetchUsers() {
      axios.get('/api/users').then(r => {
        this.users = r.data.users || []
      }).catch(error => {
        console.error('Load users error:', error)
        this.$message.error('加载用户列表失败')
      })
    },
    deleteUser(user) {
      this.$confirm(`确认删除用户 ${user.username} 吗？`, '删除用户', {
        type: 'warning'
      }).then(() => {
        axios.post(`/api/users/${user.id}/delete`).then(() => {
          this.$message.success('删除成功')
          this.fetchUsers()
        }).catch(() => {
          this.$message.error('删除用户失败')
        })
      }).catch(() => {
      })
    }
  }
}
</script>

<style scoped>
.page-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.main-card {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}
</style>