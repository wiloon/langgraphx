# Multi-Root Workspace Guide

## What is Multi-Root Workspace?

VS Code Multi-Root Workspace 允许你在一个窗口中同时打开多个项目，非常适合：
- AI agent 需要跨项目操作
- 同时开发和部署多个相关项目
- 保持各项目 git 仓库独立

## Setup

### 1. Open the Workspace

有两种方式打开：

**方式 A: 从命令行**
```bash
cd /Users/wiloon/workspace/projects/langgraphx
code langgraphx-development.code-workspace
```

**方式 B: 从 VS Code**
1. File → Open Workspace from File...
2. 选择 `langgraphx-development.code-workspace`

### 2. 工作区结构

打开后你会看到 3 个项目根目录：

```
🤖 langgraphx (AI System)     # AI 开发系统
├── src/
├── tests/
├── scripts/
└── .venv/                    # Python 虚拟环境

📰 rssx (RSS Project)          # RSS 项目
├── api/                      # Go backend
└── ui/                       # TypeScript frontend

🏠 w10n-config (Homelab)       # 部署配置
└── homelab/k8s/
    ├── rssx/                 # rssx 的 K8s manifests
    └── ...
```

## Features

### 🎯 已配置功能

#### 1. **Python 环境自动识别**
- langgraphx 的 `.venv` 自动激活
- 类型检查和智能提示开箱即用

#### 2. **多语言支持**
- **Python** (langgraphx): Black formatter, Ruff linter
- **Go** (rssx-api): 自动格式化, gofmt
- **TypeScript** (rssx-ui): Prettier formatter, ESLint

#### 3. **内置任务 (Tasks)**

按 `Cmd+Shift+P` → "Run Task" 可以运行：

| 任务 | 命令 | 说明 |
|------|------|------|
| 🤖 Run LangGraphX | `uv run python -m src.main` | 启动 AI 系统 |
| 🧪 Run Tests | `uv run pytest tests/ -v` | 运行测试 |
| ✅ Verify Setup | `python scripts/verify_setup.py` | 验证环境 |
| 🏗️ Build rssx-api | `cd api && go build` | 编译 Go 后端 |
| 🧪 Test rssx-api | `cd api && go test ./...` | 测试 Go 后端 |
| 🎨 Build rssx-ui | `cd ui && pnpm build` | 构建前端 |
| 🚀 Dev rssx-ui | `cd ui && pnpm dev` | 启动前端开发服务器 |

#### 4. **调试配置 (Launch Configurations)**

按 `F5` 或在 Run and Debug 面板选择：

- 🤖 **Run LangGraphX** - 调试 AI 系统
- 🧪 **Run Tests** - 调试测试
- ✅ **Verify Setup** - 调试验证脚本

#### 5. **推荐扩展**

Workspace 会自动推荐安装：
- Python 开发工具 (Pylance, Black, Ruff)
- Go 开发工具
- TypeScript 开发工具 (Prettier, ESLint)
- Docker & Kubernetes 工具
- Git 工具 (GitLens)

## Usage Examples

### 示例 1: AI Agent 修改 rssx 代码

1. **在 langgraphx 中启动 AI 系统**:
   ```bash
   # Terminal 1 (langgraphx)
   uv run python -m src.main
   ```

2. **AI 读取 rssx 代码**:
   - agent 使用 `read_file` 工具
   - 路径: `/Users/wiloon/workspace/projects/rssx/api/main.go`
   - 在左侧 `📰 rssx` 目录中立即可见

3. **AI 写入修改**:
   - agent 使用 `write_file` 工具修改文件
   - 修改立即显示在 rssx 编辑器中
   - Git 变更实时显示在 Source Control 面板

### 示例 2: 跨项目查找

使用全局搜索 (`Cmd+Shift+F`) 可以同时搜索所有 3 个项目：

```
搜索: "RSS"
结果:
  🤖 langgraphx: projects/rssx/config.yaml
  📰 rssx: api/handlers/feed.go
  🏠 w10n-config: homelab/k8s/rssx/deployment.yaml
```

### 示例 3: 同时开发和部署

```bash
# Terminal 1: 开发 rssx
cd rssx/ui && pnpm dev

# Terminal 2: 构建镜像
cd rssx && docker build -t rssx-ui .

# Terminal 3: 部署到 K8s
cd w10n-config/homelab/k8s/rssx
kubectl apply -f .

# Terminal 4: AI 协助开发
cd langgraphx && uv run python -m src.main
```

所有 terminals 都在一个窗口中！

## Tips

### 🎯 快捷键

| 功能 | macOS | 说明 |
|------|-------|------|
| 切换项目文件夹 | `Cmd+K Cmd+P` | 快速切换 |
| 全局搜索 | `Cmd+Shift+F` | 跨所有项目 |
| 运行任务 | `Cmd+Shift+P` → Run Task | 执行预定义任务 |
| 切换 Terminal | `Ctrl+` ` | 在 terminals 间切换 |

### 📁 文件导航

使用 Breadcrumbs 区分文件来自哪个项目：
```
🤖 langgraphx > src > agents > developer.py
📰 rssx > api > main.go
🏠 w10n-config > homelab > k8s > rssx > deployment.yaml
```

### 🔍 特定项目搜索

在搜索框下方的 "files to include" 中指定：
```
./rssx/**/*.go        # 只搜索 rssx 的 Go 文件
./langgraphx/src/**   # 只搜索 langgraphx 源码
```

## Git Management

### 每个项目独立的 Git

Source Control 面板会显示 3 个仓库：

```
SOURCE CONTROL
├─ 🤖 langgraphx (main)
│  └─ Changes: 3 files
├─ 📰 rssx (develop)
│  └─ Changes: 2 files
└─ 🏠 w10n-config (main)
   └─ No changes
```

### 提交策略

推荐分别提交：
- **langgraphx**: AI 系统本身的改进
- **rssx**: AI 生成的业务代码
- **w10n-config**: 部署配置的更新

## Troubleshooting

### Python 环境未激活

如果 Python 提示找不到模块：
1. `Cmd+Shift+P` → "Python: Select Interpreter"
2. 选择 `./venv/bin/python` (在 langgraphx 目录下)

### Go 模块问题

如果 Go 提示找不到模块：
```bash
cd /Users/wiloon/workspace/projects/rssx/api
go mod tidy
```

### TypeScript 配置

如果 TypeScript 有问题：
```bash
cd /Users/wiloon/workspace/projects/rssx/ui
pnpm install
```

## Benefits

### ✅ 对 AI Agent 开发的优势

1. **可见性**: Agent 修改 rssx 代码时，你立即看到变化
2. **调试**: 可以同时调试 langgraphx 和 rssx
3. **版本控制**: 三个独立的 git 仓库，清晰分离
4. **效率**: 不用切换窗口，所有项目一个视图
5. **集成**: Tasks 和 Launch configs 一键运行

### ✅ 对开发部署的优势

1. 同时看到代码、部署配置、AI 系统
2. 修改代码 → 更新 K8s manifest → 部署，流程顺畅
3. 跨项目搜索和重构
4. 统一的编辑器设置和扩展

---

**下一步**: 
1. 打开 workspace: `code langgraphx-development.code-workspace`
2. 安装推荐的扩展
3. 运行 `🤖 Run LangGraphX` 任务测试系统
