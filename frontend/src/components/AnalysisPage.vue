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
                    <DataAnalysis/>
                  </el-icon>
                  <span>技术分析</span>
                </div>
              </template>
              <el-tabs v-model="activeTab" type="border-card">
                <el-tab-pane label="技术要素提取" name="elements">
                  <el-form class="filter-form" inline>
                    <el-form-item label="选择专利">
                      <el-select v-model="selectedPatents" filterable multiple placeholder="选择要分析的专利"
                                 style="width:400px;">
                        <el-option v-for="p in patents" :key="p.id" :label="p.title.substring(0,50) + '...' "
                                   :value="p.id"></el-option>
                      </el-select>
                    </el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="extractElements">
                        <el-icon>
                          <Search/>
                        </el-icon>
                        提取要素
                      </el-button>
                    </el-form-item>
                  </el-form>
                  <div v-for="result in elementResults" :key="result.patent_id" class="analysis-result">
                    <el-divider>{{ getPatentTitle(result.patent_id) }}</el-divider>
                    <el-row :gutter="20">
                      <el-col :span="6">
                        <el-card class="element-card" size="small">
                          <template #header>
                            <el-icon>
                              <Lightning/>
                            </el-icon>
                            技术
                          </template>
                          <div class="element-list">
                            <el-tag v-for="tech in result.elements.technologies" :key="tech" size="small"
                                    type="success">{{ tech }}
                            </el-tag>
                          </div>
                        </el-card>
                      </el-col>
                      <el-col :span="6">
                        <el-card class="element-card" size="small">
                          <template #header>
                            <el-icon>
                              <Warning/>
                            </el-icon>
                            问题
                          </template>
                          <div class="element-list">
                            <el-tag v-for="prob in result.elements.problems" :key="prob" size="small" type="danger">
                              {{ prob }}
                            </el-tag>
                          </div>
                        </el-card>
                      </el-col>
                      <el-col :span="6">
                        <el-card class="element-card" size="small">
                          <template #header>
                            <el-icon>
                              <Check/>
                            </el-icon>
                            解决方案
                          </template>
                          <div class="element-list">
                            <el-tag v-for="sol in result.elements.solutions" :key="sol" size="small" type="info">{{
                                sol
                              }}
                            </el-tag>
                          </div>
                        </el-card>
                      </el-col>
                      <el-col :span="6">
                        <el-card class="element-card" size="small">
                          <template #header>
                            <el-icon>
                              <Star/>
                            </el-icon>
                            优势
                          </template>
                          <div class="element-list">
                            <el-tag v-for="adv in result.elements.advantages" :key="adv" size="small" type="warning">
                              {{ adv }}
                            </el-tag>
                          </div>
                        </el-card>
                      </el-col>
                    </el-row>
                  </div>
                </el-tab-pane>

                <el-tab-pane label="专利地图" name="map">
                  <el-form class="filter-form" inline>
                    <el-form-item label="选择专利">
                      <el-select v-model="selectedPatents" filterable multiple
                                 placeholder="选择要生成地图的专利" style="width:400px;">
                        <el-option v-for="p in patents" :key="p.id" :label="p.title.substring(0,50) + '...' "
                                   :value="p.id"></el-option>
                      </el-select>
                    </el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="generateMap">
                        <el-icon>
                          <Picture/>
                        </el-icon>
                        生成专利地图
                      </el-button>
                    </el-form-item>
                  </el-form>
                  <div v-if="mapImage" class="map-container">
                    <img :src="'data:image/png;base64,' + mapImage" alt="专利地图" class="map-image">
                  </div>
                </el-tab-pane>

                <el-tab-pane label="技术机会" name="opportunities">
                  <el-form class="filter-form" inline>
                    <el-form-item>
                      <el-button type="primary" @click="findOpportunities">
                        <el-icon>
                          <Opportunity/>
                        </el-icon>
                        识别技术机会
                      </el-button>
                    </el-form-item>
                  </el-form>
                  <el-table :data="opportunities" :header-cell-style="{background:'#f5f7fa', color:'#606266'}" stripe
                            style="width: 100%; margin-top:20px;">
                    <el-table-column label="技术领域" min-width="150" prop="technology"></el-table-column>
                    <el-table-column align="center" label="机会评分" prop="opportunity_score" width="120">
                      <template #default="{ row }">
                        <el-tag :type="row.opportunity_score > 5 ? 'success' : 'warning'">{{
                            row.opportunity_score
                          }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column label="原因" min-width="200" prop="reason"></el-table-column>
                  </el-table>
                </el-tab-pane>
              </el-tabs>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import axios from 'axios'
import AppHeader from './AppHeader.vue'
import {Check, DataAnalysis, Lightning, Opportunity, Picture, Star, Warning} from '@element-plus/icons-vue'

export default {
  components: {AppHeader, DataAnalysis, Lightning, Warning, Check, Star, Picture, Opportunity},
  data() {
    return {
      activeTab: 'elements',
      patents: [],
      selectedPatents: [],
      elementResults: [],
      mapImage: '',
      opportunities: []
    }
  },
  mounted() {
    this.fetchPatents()
    // 如果有专利ID参数，自动选择
    const patentId = this.$route.query.patent_id
    if (patentId) {
      this.selectedPatents = [parseInt(patentId)]
    }
  },
  methods: {
    fetchPatents() {
      axios.get('/api/patents', {params: {page: 1, per: 100}}).then(r => {
        this.patents = r.data.rows
      })
    },
    extractElements() {
      if (!this.selectedPatents.length) {
        this.$message.warning('请先选择专利')
        return
      }
      axios.post('/api/patents/analyze', {patent_ids: this.selectedPatents, type: 'elements'}).then(r => {
        this.elementResults = r.data.results
        this.$message.success('要素提取完成')
      })
    },
    generateMap() {
      if (!this.selectedPatents.length) {
        this.$message.warning('请先选择专利')
        return
      }
      axios.post('/api/patents/analyze', {patent_ids: this.selectedPatents, type: 'map'}).then(r => {
        this.mapImage = r.data.image
        this.$message.success('专利地图生成完成')
      })
    },
    findOpportunities() {
      axios.post('/api/patents/analyze', {patent_ids: this.patents.map(p => p.id), type: 'opportunities'}).then(r => {
        this.opportunities = r.data.opportunities
        this.$message.success('技术机会识别完成')
      })
    },
    getPatentTitle(id) {
      const patent = this.patents.find(p => p.id === id)
      return patent ? patent.title : '未知专利'
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

.analysis-result {
  margin-bottom: 30px;
}

.element-card {
  height: 200px;
  overflow: hidden;
}

.element-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  max-height: 140px;
  overflow-y: auto;
}

.map-container {
  margin-top: 20px;
  text-align: center;
}

.map-image {
  max-width: 100%;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}
</style>