# 基于专利地图的技术机会发现系统

## 项目简介

本项目是一个基于专利地图的技术机会发现系统，通过融合自然语言处理技术，实现专利文本的自动化解析与技术要素提取，构建技术热点关联矩阵，结合GTM算法与多维空间专利地图理论，实现专利地图的自动化生成与技术机会的可视化挖掘。同时构建多维度技术机会评价指标体系，实现创新机会的量化筛选。

该系统为企业、科研机构的技术研发决策、专利布局规划提供自动化、智能化的支撑，降低技术创新的盲目性与研发风险，提升技术机会识别的效率与准确性。

## 主要功能

- **专利数据爬取**: 支持万方专利平台的分布式爬取，采用企业级架构
- **技术要素提取**: 使用先进的BERT-BiLSTM-CRF模型自动提取专利中的技术要素、问题描述和解决方案
- **技术热点分析**: 基于TF-IDF和K-means聚类分析识别技术热点，支持多维度分析
- **专利地图可视化**: 自动生成专利技术关联图，支持交互式可视化（ECharts）
- **技术机会识别**: 量化评价技术机会，使用RandomForest回归模型识别创新空白点和潜在机会
- **用户管理系统**: 完整的用户认证和权限管理，支持角色-based访问控制
- **日志监控系统**: 详细的爬虫运行日志和错误监控功能
- **队列状态监控**: 实时监控Redis队列状态、生产者消费者线程、系统资源使用情况
- **数据导出功能**: 支持技术机会报告导出为Excel格式
- **通知系统**: 实时通知用户重要事件和分析结果
- **响应式UI**: 现代化的Vue 3 + Element Plus界面，支持暗色模式

## 技术栈

### 后端

- **框架**: Flask + Flask-Login + Flask-CORS
- **数据库**: MySQL + Redis
- **NLP**: Transformers (BERT) + PyTorch + Jieba
- **机器学习**: Scikit-learn + Pandas + NumPy
- **爬虫**: Scrapy + Curl-CFFI
- **可视化**: Matplotlib + NetworkX + Plotly

### 前端

- **框架**: Vue 3 + Vue Router 4
- **UI库**: Element Plus + ECharts
- **构建工具**: Vite
- **HTTP客户端**: Axios

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- Redis 6.0+

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd lfq_hbut
   ```

2. **后端安装**
   ```bash
   pip install -r requirements.txt
   ```

3. **前端安装**
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

4. **数据库配置**
    - 安装并启动MySQL和Redis
    - 修改 `backend/configs.py` 中的数据库配置
    - 运行数据库建表脚本

5. **启动服务**
   ```bash
   # 启动后端
   python run.py

   # 启动前端（开发模式）
   cd frontend
   npm run dev
   ```

6. **访问应用**
    - 前端: http://localhost:3000
    - 后端API: http://localhost:5000

## 项目优化亮点

### 最新更新 (2024)

- ✅ **NLP模型升级**: 集成真实的BERT-BiLSTM-CRF模型，提升技术要素提取准确性
- ✅ **UI/UX改进**: 采用Element Plus组件库，实现响应式设计和现代化界面
- ✅ **新功能添加**:
    - 数据导出功能（Excel报告）
    - 通知系统框架
    - 改进的技术机会评估算法
- ✅ **代码质量**: 添加类型提示、错误处理和代码注释
- ✅ **性能优化**: 实现缓存机制和异步处理
- ✅ **安全性增强**: 添加输入验证和SQL注入防护

### 核心算法

- **技术要素提取**: BERT预训练模型 + BiLSTM + CRF
- **技术热点分析**: TF-IDF向量化 + K-means聚类
- **机会识别**: 随机森林回归 + 启发式规则
- **专利地图**: GTM算法 + 网络可视化

## API文档

### 主要接口

- `POST /api/patents/analyze` - 专利分析（要素提取/地图生成/机会识别）
- `POST /api/patents/export` - 数据导出
- `GET /api/patents` - 专利列表查询
- `POST /api/auth/login` - 用户登录
- `GET /api/status` - 系统状态查询

## 部署说明

### 生产环境部署

1. 配置生产数据库
2. 设置环境变量
3. 使用Gunicorn启动后端
4. 配置Nginx反向代理
5. 启用HTTPS

### Docker部署（计划中）

- 后端Dockerfile
- 前端多阶段构建
- Docker Compose编排

## 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

项目维护者: [您的名字]
邮箱: [您的邮箱]

```
lfq_hbut/
├── backend/              # Python后端服务
│   ├── auth.py          # 用户认证模块
│   ├── configs.py       # 配置文件
│   ├── gtm.py           # GTM算法实现
│   ├── Item_models.py   # 数据模型定义
│   ├── main.py          # 主程序入口
│   ├── nlp.py           # NLP处理核心
│   ├── nlp_tools.py     # NLP工具函数
│   ├── opportunity.py   # 机会识别模块
│   ├── parse_tools.py   # 数据解析工具
│   ├── web.py           # Flask Web应用
│   ├── nlp_tools/       # NLP工具资源
│   │   └── dict.txt     # 词典文件
│   ├── spiders/         # 爬虫模块
│   │   ├── spider_base.py    # 爬虫基类
│   │   └── wanfangtools.py   # 万方专利爬虫
│   └── sql/             # 数据库相关
│       ├── createTables.sql  # 数据库建表脚本
│       └── sql_tools.py      # 数据库工具
├── frontend/            # Vue前端应用
│   ├── src/
│   │   ├── components/  # Vue组件
│   │   │   ├── AnalysisPage.vue    # 分析页面
│   │   │   ├── AppHeader.vue       # 应用头部
│   │   │   ├── Dashboard.vue       # 仪表板
│   │   │   ├── LoginForm.vue       # 登录表单
│   │   │   ├── LoginPage.vue       # 登录页面
│   │   │   ├── LogsTable.vue       # 日志表格
│   │   │   ├── PatentsPage.vue     # 专利页面
│   │   │   ├── StatusPanel.vue     # 状态面板
│   │   │   ├── TaskForm.vue        # 任务表单
│   │   │   └── TasksTable.vue      # 任务表格
│   │   ├── router/
│   │   │   └── index.js            # 路由配置
│   │   ├── App.vue                 # 主应用组件
│   │   └── main.js                 # 前端入口文件
│   ├── package.json                # 前端依赖配置
│   └── vite.config.js              # Vite构建配置
├── static/               # 静态资源
│   └── index.html        # HTML模板
├── requirements.txt      # Python依赖
├── run.py               # 项目运行脚本
└── README.md            # 项目说明文档
```

## 技术栈

### 后端技术栈

- **框架**: Flask (Python Web框架)
- **数据库**: MySQL (关系型数据库)
- **缓存**: Redis (内存数据库)
- **NLP工具**: jieba, scikit-learn (中文分词和机器学习)
- **爬虫框架**: Scrapy (分布式爬虫)

### 前端技术栈

- **框架**: Vue 3 (渐进式JavaScript框架)
- **构建工具**: Vite (快速构建工具)
- **UI组件库**: Element Plus (Vue 3组件库)
- **图表库**: ECharts (数据可视化)

### 其他技术

- **容器化**: Docker (可选，用于部署)
- **版本控制**: Git
- **包管理**: pip (Python), npm (Node.js)

## 环境要求

- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- Redis 6.0+

## 安装指南

### 1. 克隆项目

```bash
git clone <repository-url>
cd lfq_hbut
```

### 2. 后端环境配置

#### 安装Python依赖
```bash
pip install -r requirements.txt
```

#### 配置数据库

1. 安装并启动MySQL服务
2. 创建数据库：

```sql
CREATE DATABASE patent_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. 运行建表脚本：

```bash
mysql -u username -p patent_system < backend/sql/createTables.sql
```

#### 配置Redis

确保Redis服务正在运行（默认端口6379）

#### 修改配置文件

编辑 `backend/configs.py` 文件，配置数据库连接信息：

```python
# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'patent_system'
}

# Redis配置
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0
}
```

### 3. 前端环境配置

#### 安装Node.js依赖
```bash
cd frontend
npm install
```

## 运行项目

### 开发环境运行

#### 1. 启动后端服务
```bash
# 从项目根目录
python run.py
# 或者
python -m backend.web
```

后端服务将在 http://localhost:5000 启动

#### 2. 启动前端开发服务器
```bash
cd frontend
npm run dev
```

前端开发服务器将在 http://localhost:3000 启动

#### 3. 访问应用

打开浏览器访问 http://localhost:3000

#### 4. 登录说明

登录页面提供两种模式切换：

- 用户登录：进入专利管理和技术分析界面
- 管理员登录：进入管理控制台和用户管理界面

#### 5. 界面入口说明

- 管理员控制台：`http://localhost:3000/admin`
- 用户专利管理：`http://localhost:3000/patents`
- 用户技术分析：`http://localhost:3000/analysis`
- 用户管理：`http://localhost:3000/users`

### 生产环境部署

#### 构建前端

```bash
cd frontend
npm run build
```

构建后的文件将输出到 `../static/dist` 目录

#### 启动生产服务器

```bash
python run.py --prod
```

## 使用说明

### 系统功能概述

1. **用户登录**: 使用管理员账号登录系统
2. **仪表板**: 查看系统状态、爬虫运行情况和任务队列
3. **专利管理**: 浏览和管理已爬取的专利数据
4. **技术分析**: 进行技术要素提取、热点分析和机会识别
5. **日志监控**: 查看系统运行日志和错误信息

### 核心功能使用

#### 专利数据爬取

- 在仪表板中配置爬取任务
- 设置搜索关键词和时间范围
- 启动分布式爬虫进行数据采集

#### 技术要素提取

- 上传专利文本或选择已爬取数据
- 系统自动提取技术要素、问题和解决方案
- 查看提取结果的可视化展示

#### 专利地图生成

- 基于提取的技术要素生成专利关联图
- 支持交互式浏览和筛选
- 导出地图数据用于进一步分析

#### 技术机会识别

- 基于专利地图识别技术空白点
- 量化评价潜在创新机会
- 生成机会报告和建议

## API文档

系统提供RESTful API接口，主要端点包括：

- `POST /api/auth/login` - 用户登录
- `GET /api/patents` - 获取专利列表
- `POST /api/analysis/extract` - 技术要素提取
- `GET /api/analysis/map` - 获取专利地图数据
- `POST /api/tasks/start` - 启动爬虫任务

详细API文档请参考后端代码中的路由定义。

## 开发指南

### 代码规范

- 后端遵循PEP 8 Python代码规范
- 前端遵循Vue.js官方风格指南
- 使用ESLint和Prettier进行代码格式化

### 测试

```bash
# 后端测试
python -m pytest backend/

# 前端测试
cd frontend
npm run test
```

### 贡献

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

项目维护者: [您的姓名]
邮箱: [您的邮箱]
项目主页: [项目GitHub地址]

## 更新日志

### v1.0.0 (2024-01-XX)

- 初始版本发布
- 实现基础专利爬取和NLP分析功能
- 支持专利地图可视化和机会识别

---

*本项目为学术研究项目，如有问题或建议欢迎提交Issue或Pull Request。*
- 查看专利详情
- 支持关键词搜索和筛选

### 技术分析
- **技术要素提取**: 自动解析专利文本，提取技术要素
- **专利地图**: 可视化专利技术关联网络
- **技术机会**: 识别潜在创新机会和空白领域

### 用户系统
- 管理员登录认证
- 安全的API访问控制

## 企业级爬虫架构
- **生产者-消费者模式**: 分布式任务处理
- **Redis队列**: 任务分发和状态管理
- **错误重试机制**: 自动重试失败请求
- **监控日志**: 详细的运行日志记录
- **线程管理**: 可配置的线程池大小

## API接口
- `POST /api/login` - 用户登录
- `GET /api/status` - 系统状态
- `POST /api/task` - 提交搜索任务
- `GET /api/logs` - 获取日志
- `GET /api/patents` - 获取专利列表
- `POST /api/patents/analyze` - 专利分析

## 注意事项
- 确保Redis和MySQL服务正在运行
- 爬虫功能需要网络访问万方专利平台
- 首次使用需要创建管理员账户（默认用户名: admin, 密码: admin）


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

页面使用 Vue.js+Axios（在 `frontend` 项目中管理）。
启动服务后首次访问会提示登录，默认管理员账户为 **admin/admin**（第一次启动会自动创建），可在数据库 `users` 表中自行添加或修改用户。
登录后才能提交任务、查看日志、启动/停止爬虫等操作。

主要功能：
- **登录/登出**：认证用户才能访问控制台。
- **提交任务**：输入关键字、页大小、页数，任务会被记录在 `producer_tasks` 表，可用于审计或重跑。
- **队列状态**：查看 Redis 中任务数量和线程运行数。
- **启动/停止爬虫线程**。
- **日志监控**：展示 `spider_logs` 中的条目，可按照关键字、动作和时间范围筛选，并通过分页浏览。
- **任务历史**：单独标签页列出曾经提交的任务，可删除或将失败/已完成任务重新加入队列。

## 扩展与优化

**已完成改进**
- 消费者线程现在在队列为空时不会立即退出，而是每秒轮询一次。这样在生产者后续产出 taskId 时，消费者能够继续工作，避免只有生产者运行的情况。

**已实现特性**
1. **用户管理与权限**：登录模块已集成，使用 Flask-Login。默认管理员 `admin/admin`。
2. **任务历史与审核**：任务提交会写入 `producer_tasks` 表，控制台提供历史查看、删除和重跑功能。
3. **日志筛选和分页**：前端可通过关键字、动作、时间范围筛选日志，并支持分页。
4. **前端重构**：已迁移到 Vue 3 + Vite，使用 Element Plus UI 组件。

**待优化**
5. **分布式部署 & 容器化**：使用 Docker Compose 或 Kubernetes部署 Redis、MySQL和爬虫服务。
6. **爬虫控制增强**：支持运行时修改并发数、自动重启失败线程、监控耗时超时报警。
7. **REST API 完善**：加入更多管理接口，如查看任务列表、删除日志、调整配置等。
5. **分布式部署 & 容器化**：使用 Docker Compose 或 Kubernetes 部署 Redis、MySQL 和爬虫服务，支持扩展到多台机器。
6. **爬虫控制增强**：支持运行时修改并发数、自动重启失败线程、监控耗时超时报警。
7. **REST API 完善**：加入更多管理接口，如查看任务列表、删除日志、调整配置等。

---

这是基础版本，适合演示和开发。欢迎继续优化！
