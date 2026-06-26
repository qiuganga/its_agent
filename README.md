# its_agent

ITS Agent 是一个面向智能客服场景的多智能体项目，包含主调度 Agent、技术咨询专家、服务站与导航专家、知识库检索服务和前端页面。

## 项目功能

- 多智能体调度：根据用户问题选择技术专家或服务站/导航专家。
- 技术咨询：支持设备故障、维修建议、知识库问答和必要的联网搜索。
- 服务站与导航：支持附近维修站查询、位置解析、POI 解析和百度地图导航链接生成。
- 知识库服务：支持文档上传、网页抓取、向量检索和答案生成。
- 前端交互：包含智能体聊天界面和知识库管理界面。

## 当前架构

```text
FastAPI
-> MultiAgentService.process_task
-> orchestrator_agent（主调度 Agent）
-> consult_technical_expert / query_service_station_and_navigate
-> 子 Agent Runner
-> 子 Agent 本地工具 / 受控 MCP 能力
-> 子 Agent 结果作为 Tool Output 回到主 Agent
-> 主 Agent 生成最终回答
-> SSE 返回前端
```

当前架构是 Agent as Tool，不是 Handoff。主 Agent 始终保持控制权，并负责生成最终答复。

## 后端启动

```bash
cd backend/app
pip install -r requirements.txt
python api/main.py
```

## 前端启动

```bash
cd front/agent_web_ui
npm install
npm run dev
```

知识库管理前端：

```bash
cd front/knowlege_platform_ui
npm install
npm run dev
```

## 环境变量

项目运行依赖本地 `.env` 配置，例如模型 API Key、数据库连接、百度地图 AK、知识库服务地址等。

```text
backend/app/.env
backend/knowledge/.env
```

不要提交 `.env`、API Key、数据库密码或其他敏感配置。若发现代码中存在明文敏感默认值，应迁移到 `.env`。

## Harness 执行控制

本项目新增 Harness 执行控制层，用来限制 OpenAI Agents SDK 的 ReAct 循环、嵌套子 Agent 循环、重复 Tool Call，以及外部 MCP 工具的无效重复调用。

### 三层职责

- `SystemHarness`：系统级规则、工具白名单、全局并发、MCP Client 引用、结构化日志和 Session Budget Store。
- `SessionBudgetStore`：按 `(user_id, session_id)` 保存会话累计工具预算。当前为进程内临时状态，应用重启后清零；生产多实例部署应替换为 Redis 等共享存储。
- `RunHarnessState`：每次用户请求独立创建，记录本次请求的工具调用次数、子 Agent 调用次数、重复调用签名、失败次数、阻止事件和 Trace 事件。

### 为什么限制嵌套 Agent Runner

主 Agent 的两个工具会在内部启动子 Agent Runner。如果没有显式预算和去重控制，模型可能重复启动同一个子 Agent，子 Agent 又可能重复调用知识库、搜索或地图服务，导致循环、超时、费用浪费和前端长时间无结果。Harness 在所有 Agent 可见工具入口统一拦截，避免把控制逻辑只写进 Prompt。

### 默认预算与超时

- 主调度 Agent：`max_turns = 5`
- 技术 Agent：`max_turns = 4`
- 服务站 Agent：`max_turns = 5`
- 每个 Run 的 Agent 可见工具总调用数：`8`
- 每个 Run 的子 Agent Tool 调用数：`2`
- 每个请求最长执行时间：`45` 秒
- 全局并发 Run：`20`
- Session Budget TTL：`30` 分钟
- Session 工具总调用预算：`80`

子 Agent Tool 默认每个 Run 最多调用一次：

- `consult_technical_expert`
- `query_service_station_and_navigate`

低层工具默认每个 Run 最多调用一次：

- `query_knowledge`
- `search_web`
- `resolve_user_location_from_text`
- `query_nearest_repair_shops_by_coords`
- `geocode_destination`
- `map_navigation_tool`

### Tool 去重规则

同一个 Run 内，Harness 会对以下内容生成规范化签名：

```text
agent_name + tool_name + canonical JSON arguments
```

字符串会去除首尾空白，并归一化内部连续空白；字典按 key 排序后序列化。相同签名第二次出现时不会再访问真实服务，而是返回结构化 `harness_blocked` 结果，提示模型使用已有结果生成最终答复。

### MCP 暴露策略

子 Agent 不再直接拥有完整 MCP Server。Agent 只能看到经过 Harness 包装的 Python Function Tool：

- 技术 Agent：`query_knowledge`、`search_web`
- 服务站 Agent：`resolve_user_location_from_text`、`query_nearest_repair_shops_by_coords`、`geocode_destination`、`map_navigation_tool`

搜索 MCP 仅允许 `bailian_web_search`。百度 MCP 仅允许 `map_geocode`、`map_ip_location`、`map_uri`。这些 MCP 调用只能由受控 Python Tool 内部执行，不能直接暴露给模型。

### 测试

运行 Harness 测试：

```bash
cd backend
python -m unittest app.tests.test_harness_control
```

编译检查：

```bash
cd backend
python -m compileall app
```

## 注意事项

- Harness 不是 OS 级 Sandbox。本项目没有新增 Shell、文件编辑、电脑控制类工具，也不允许 Agent Tool 读取 `.env`、执行终端命令或任意访问文件系统。
- FastAPI lifespan 仍负责应用启动时连接 MCP、关闭时清理 MCP。
- 如果 MCP 工具提示 `Server not initialized`，优先检查 MCP client 是否在应用启动时成功连接。
