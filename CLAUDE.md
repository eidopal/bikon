# BIKON Marketing API

## 技术栈
- Python 3.11+ / FastAPI / SQLAlchemy (async) / SQLite
- OpenRouter API (Google Gemini) - AI 文案生成
- Pillow - 图片水印
- python-jose - JWT token 签发
- 微信小程序 API (code2session / 内容安全)

## 项目结构
```
app/
  main.py              - FastAPI 入口
  database.py          - 异步 SQLAlchemy engine + session
  core/
    config.py          - pydantic-settings (环境变量)
    logging_config.py  - 日志配置
    auth.py            - JWT 签发 + 鉴权依赖 (get_current_user)
  models/
    task.py            - 任务模型 (PENDING → PROCESSING → COMPLETED/FAILED)
    merchant.py        - 商户模型
    brand_asset.py     - 品牌资产模型
    user.py            - 微信用户模型 (openid, merchant_id)
  api/v1/
    production.py      - 营销生产任务 API (URL提交 / 文件上传 / 任务列表)
    merchant.py        - 商户 CRUD API (需鉴权)
    wechat.py          - 微信小程序 API (登录/安全审查)
  services/
    task_service.py    - 任务编排 + 后台处理
    ai_service.py      - AI 文案 + 音频转写
    visual_engine.py   - 图片水印
    wechat_service.py  - 微信 access_token + 安全审查
  utils/
    response.py        - 统一响应格式 + 全局异常处理
    storage.py         - 文件上传/删除
tests/
    conftest.py        - test fixtures + auth override
    test_task.py       - 任务 API 测试 (6 tests)
    test_task_concurrent.py - 并发生成测试
    test_task_service_logic.py - 任务服务单元测试
    test_merchant.py   - 商户 API 测试
    test_wechat.py     - 微信 API 测试
    test_visual_engine.py - 水印引擎测试
    test_ai_service.py - AI 文案测试 (mock)
    test_full_workflow.py - 端到端集成测试
```

## 分支规范

```
master         - 生产分支，始终可部署
feature/xxx    - 新功能开发
fix/xxx        - bug 修复
refactor/xxx   - 重构
test/xxx       - 测试补充
```

规则：
- 从 `master` 切出新分支
- 分支名用小写 + 短横线，如 `feature/task-queue`, `fix/watermark-crash`
- 合并回 `master` 通过 PR
- 提交信息用祈使句（如 "Add", "Fix", "Refactor"），不要用过去式

## 提交信息规范

```
<动词> <简短描述>

<可选的详细说明>
```

示例：
- `Add Redis task queue for background jobs`
- `Fix session leak in background task processing`
- `Refactor watermark to support custom positions`

## 常用命令

```bash
# 启动开发服务器
uvicorn app.main:app --reload --port 8000

# 运行测试
pytest -v

# 运行单个测试文件
pytest tests/test_task.py -v

# 数据库重置（删除 SQLite 文件重新建表）
rm -f bikon.db && uvicorn app.main:app
```

## 已知待办

- [ ] Redis 任务队列（当前裸用 asyncio.create_task）
- [ ] Docker 部署
- [ ] CI/CD (GitHub Actions)
- [ ] 商户列表/删除接口
- [ ] WebSocket 任务完成推送
- [ ] 微信小程序前端页面
