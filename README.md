# lfq_hbut 爬虫项目

## 项目结构
```
lfq_hbut/
├─backend/          # Python 后端包
│   ├─configs.py
│   ├─Item_models.py
│   ├─main.py
│   ├─web.py
│   ├─parse_tools.py
│   ├─sql/
│   └─spiders/
├─frontend/         # Vue + Vite 前端项目
├─static/           # 静态资源（前端构建输出）
├─README.md
└─requirements.txt
```

此项目用于从万方专利平台抓取专利数据，支持生产者/消费者模式、Redis 任务队列、MySQL 日志存储。
后端代码位于 `backend/` 包中，前端为一个独立的 Vue + Vite 应用位于 `frontend/`。
## 安装依赖

### Python 后端
```bash
pip install -r requirements.txt
```

### 前端 Vue 项目
在 `frontend` 目录下执行（需安装 Node.js/npm）：
```bash
cd frontend
npm install
npm run dev        # 开发模式，访问 http://localhost:3000
npm run build      # 生产构建，输出到 ../static/dist
```
后端的 Flask 会将 `static/dist/index.html` 作为主页提供。


## 数据库

执行 `sql/createTables.sql`，创建 `patent_basic`、`spider_logs` 等表。

## Redis

默认配置 localhost:6379，无需额外设置。

## 启动爬虫和控制台

1. **启动前端开发服务器（可选）**
   ```bash
   cd frontend
   npm run dev
   ```
   默认地址 http://localhost:3000，可按需修改 API 前缀或代理。

2. **启动后端 Flask 服务**
   ```bash
   # 进入项目根目录，使用包方式运行
   python -m backend.web
   # 或者直接执行脚本
   # python backend/web.py
   ```
   在开发模式下访问由前端提供的页面。生产构建时，使用 `npm run build` 将前端内容输出到 `static/dist`，Flask 会自动返回该静态文件。

3. **通过控制台** 提交任务、查看队列、启动/停止线程和监控日志。

4. 使用 `/api/start` 等 REST 端点编程控制。

## 管理员页面说明

页面使用 Vue.js+Axios（CDN 引入）。主要功能：
- 提交任务：输入关键字、页大小、页数（前端使用 Element Plus UI 组件）。
- 队列状态：查看 Redis 中任务数量和线程运行数量。
- 启动/停止爬虫线程。
- 日志监控：从 `spider_logs` 读取并展示最近记录。

## 扩展与优化

**已完成改进**
- 消费者线程现在在队列为空时不会立即退出，而是每秒轮询一次。这样在生产者后续产出 taskId 时，消费者能够继续工作，避免只有生产者运行的情况。

**后续建议**
1. **用户管理与权限**：添加登录模块，只有认证用户才能提交任务或查看日志；可使用 Flask-Login 或 JWT。
2. **任务历史与审核**：保留已提交任务记录，提供界面查看/删除，并支持任务重跑。
3. **日志筛选和分页**：前端增加按照关键词、动作、时间范围筛选日志，并实现翻页。
4. **前端重构**：将静态页面迁移到 Vue CLI / Vite 或 Nuxt，使用组件库（如 Element Plus、Ant Design Vue）提升体验。
5. **分布式部署 & 容器化**：使用 Docker Compose 或 Kubernetes 部署 Redis、MySQL 和爬虫服务，支持扩展到多台机器。
6. **爬虫控制增强**：支持运行时修改并发数、自动重启失败线程、监控耗时超时报警。
7. **REST API 完善**：加入更多管理接口，如查看任务列表、删除日志、调整配置等。

---

这是基础版本，适合演示和开发。欢迎继续优化！
