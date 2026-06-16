# its_agent

ITS Agent 是一个面向智能客服场景的多智能体项目，包含主调度智能体、技术咨询专家、服务站与导航专家，以及知识库检索服务和两个 Vue 前端页面。

## 项目功能

- 多智能体调度：根据用户问题自动选择技术专家或服务站专家。
- 技术咨询：支持电脑故障、维修建议、实时资讯等问题处理。
- 服务站与导航：支持附近维修站查询、位置解析和百度地图导航链接生成。
- 知识库服务：支持文档上传、网页抓取、向量检索和答案生成。
- 前端交互：包含智能体聊天界面和知识库管理界面。

## 目录结构

```text
its_multi_agent/
├── backend/
│   ├── app/                         # 多智能体后端 API
│   ├── knowledge/                   # 知识库/RAG 服务
│   └── openai-agents-tutorial/      # OpenAI Agents 示例代码
└── front/
    ├── agent_web_ui/                # 智能体聊天前端
    └── knowlege_platform_ui/        # 知识库管理前端
```

## 后端启动

安装智能体后端依赖：

```bash
cd backend/app
pip install -r requirements.txt
```

启动智能体 API：

```bash
python api/main.py
```

安装知识库服务依赖：

```bash
cd backend/knowledge
pip install -r requirements.txt
```

启动知识库 API：

```bash
python api/main.py
```

## 前端启动

启动智能体聊天前端：

```bash
cd front/agent_web_ui
npm install
npm run dev
```

启动知识库管理前端：

```bash
cd front/knowlege_platform_ui
npm install
npm run dev
```

## 环境变量

项目运行依赖本地 `.env` 配置，例如模型 API Key、数据库连接、百度地图 AK、知识库服务地址等。

`.env` 文件不会提交到 GitHub。首次部署时请根据本地配置自行创建：

```text
backend/app/.env
backend/knowledge/.env
```

## 注意事项

- `node_modules`、`.env`、日志、缓存、数据库文件和向量库产物已通过 `.gitignore` 排除。
- 如果 MCP 工具提示 `Server not initialized`，优先检查 MCP client 是否在应用启动时正确连接，以及导入路径是否统一使用 `app.infrastructure...`。
- 本项目包含本地知识库数据文件，首次推送体积可能较大。
