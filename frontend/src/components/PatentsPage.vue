<template>
  <div class="page-container">
    <el-container style="height:100vh;">
      <AppHeader/>
      <el-main class="page-main">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-card class="main-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <el-icon>
                    <Document/>
                  </el-icon>
                  <span>专利管理</span>
                </div>
              </template>
              <el-form :model="filter" class="filter-form" inline @submit.prevent="search">
                <el-form-item label="关键词">
                  <el-input v-model="filter.keyword" clearable placeholder="标题关键词"
                            @keyup.enter="search"></el-input>
                </el-form-item>
                <el-form-item label="申请人">
                  <el-input v-model="filter.applicant" clearable placeholder="申请人名称"
                            @keyup.enter="search"></el-input>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="search">
                    <el-icon>
                      <Search/>
                    </el-icon>
                    搜索
                  </el-button>
                </el-form-item>
              </el-form>
              <el-table :data="patents" :header-cell-style="{background:'#f5f7fa', color:'#606266'}" stripe style="width: 100%"
                        @row-click="showDetail" @row-dblclick="analyzePatent">
                <el-table-column align="center" label="ID" prop="id" width="80"></el-table-column>
                <el-table-column label="标题" min-width="300" prop="title" show-overflow-tooltip>
                  <template #default="{ row }">
                    <div class="title-cell">
                      <strong>{{ row.title }}</strong>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="申请人" min-width="150" prop="applicant"
                                 show-overflow-tooltip></el-table-column>
                <el-table-column align="center" label="公开日" prop="publication_date" width="120"></el-table-column>
                <el-table-column align="center" label="国别" prop="country_code" width="80">
                  <template #default="{ row }">
                    <el-tag size="small">{{ row.country_code }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column align="center" fixed="right" label="操作" width="150">
                  <template #default="{ row }">
                    <el-button size="mini" type="primary" @click.stop="analyzePatent(row)">
                      <el-icon>
                        <DataAnalysis/>
                      </el-icon>
                      分析
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              <div class="pagination-wrapper">
                <el-pagination
                    :current-page.sync="page"
                    :page-size="per"
                    :page-sizes="[10, 20, 50, 100]"
                    :total="total"
                    background
                    layout="prev, pager, next, sizes"
                    @current-change="changePage"
                    @size-change="changeSize"
                ></el-pagination>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 专利详情对话框 -->
        <el-dialog v-model="detailVisible" :before-close="handleClose" title="专利详情" width="80%">
          <div v-if="currentPatent" class="patent-detail">
            <el-descriptions :column="2" border>
              <el-descriptions-item :span="2" label="标题">{{ currentPatent.title }}</el-descriptions-item>
              <el-descriptions-item label="申请号">{{ currentPatent.application_number }}</el-descriptions-item>
              <el-descriptions-item label="公开号">{{ currentPatent.publication_number }}</el-descriptions-item>
              <el-descriptions-item label="申请人">{{ currentPatent.applicant }}</el-descriptions-item>
              <el-descriptions-item label="发明人">{{ currentPatent.inventors }}</el-descriptions-item>
              <el-descriptions-item label="公开日">{{ currentPatent.publication_date }}</el-descriptions-item>
              <el-descriptions-item :span="2" label="摘要">
                <el-text>{{ currentPatent.abstract_text }}</el-text>
              </el-descriptions-item>
              <el-descriptions-item v-if="currentPatent.full_text" :span="2" label="全文">
                <el-text>{{ currentPatent.full_text.description_text }}</el-text>
              </el-descriptions-item>
            </el-descriptions>
          </div>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="detailVisible = false">关闭</el-button>
            </span>
          </template>
        </el-dialog>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import axios from 'axios'
import AppHeader from './AppHeader.vue'
import {DataAnalysis, Document, Search} from '@element-plus/icons-vue'

export default {
  components: {AppHeader, Document, Search, DataAnalysis},
  data() {
    return {
      patents: [],
      total: 0,
      page: 1,
      per: 20,
      filter: {keyword: '', applicant: ''},
      detailVisible: false,
      currentPatent: null
    }
  },
  mounted() {
    this.fetchPatents()
  },
  methods: {
    fetchPatents() {
      const params = {page: this.page, per: this.per, ...this.filter}
      axios.get('/api/patents', {params}).then(r => {
        this.patents = r.data.rows
        this.total = r.data.total
      }).catch(error => {
        this.$message.error('加载专利列表失败')
        console.error('Error fetching patents:', error)
      })
    },
    search() {
      this.page = 1
      this.fetchPatents()
    },
    changePage(page) {
      this.page = page
      this.fetchPatents()
    },
    changeSize(size) {
      this.per = size
      this.page = 1
      this.fetchPatents()
    },
    showDetail(row) {
      // 显示加载状态
      this.$message.loading('加载专利详情中...', 0)
      axios.get(`/api/patents/${row.id}`).then(r => {
        this.currentPatent = r.data
        this.detailVisible = true
        this.$message.closeAll()
      }).catch(error => {
        this.$message.closeAll()
        this.$message.error('加载专利详情失败')
        console.error('Error loading patent detail:', error)
      })
    },
    handleClose() {
      this.detailVisible = false
      this.currentPatent = null
    },
    analyzePatent(row) {
      // 跳转到分析页面，传递专利ID
      this.$router.push({name: 'Analysis', query: {patent_id: row.id}})
    }
  }
}
</script>

<style scoped>
.page-container {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.page-main {
  background: #f5f7fa;
  padding: 20px;
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

.filter-form {
  margin-bottom: 20px;
}

.pagination-wrapper {
  text-align: right;
  margin-top: 20px;
}

.patent-detail {
  max-height: 60vh;
  overflow-y: auto;
}

.title-cell {
  font-weight: 500;
  color: #303133;
}

.el-table {
  border-radius: 8px;
  overflow: hidden;
}

.el-table th {
  background-color: #f5f7fa !important;
  color: #606266 !important;
  font-weight: 600;
}

.el-table td {
  padding: 12px 8px;
}

.el-pagination {
  margin-top: 20px;
  text-align: right;
}
</style>