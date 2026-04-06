<template>
  <div id="app">
    <router-view/>
  </div>
</template>

<script>
import AppLayout from './components/AppLayout.vue'

export default {
  components: {AppLayout}
}
</script>

<style>
/* global styles */
* {
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  height: 100vh;
}

/* Element Plus 样式覆盖 */
.el-header {
  padding: 0 20px;
}

.el-aside {
  padding: 0;
}

.el-main {
  padding: 0;
}

/* 确保表格头部可见 */
.el-table th {
  background-color: #f5f7fa !important;
  color: #606266 !important;
  border-bottom: 1px solid #ebeef5 !important;
}

.el-table--border th {
  border-right: 1px solid #ebeef5 !important;
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>