# 开发快速测试指南

## 命令行直接运行

### 基本用法

```bash
# 交互模式（原来的方式）
uv run python -m src.main

# 直接执行任务
uv run python -m src.main "你的任务描述"

# 指定项目执行任务
uv run python -m src.main -p w10n-config "查看 rssx Ingress 配置"

# 列出所有项目
uv run python -m src.main --list-projects
```

### 参数说明

```
-p, --project    指定项目 (rssx, enx, w10n-config)
-l, --list-projects    列出所有项目并退出
-h, --help       显示帮助信息
```

---

## 使用 Task 快捷命令

### 查看所有任务

```bash
task --list
# 或
task help
```

### 预定义测试任务

```bash
# 验证系统设置
task verify

# 运行测试
task test

# 运行交互模式
task run
```

### 快速测试任务

```bash
# 测试 w10n-config 的 Ingress 配置
task test:check-ingress

# 测试修改 Ingress 证书
task test:modify-ingress

# 测试列出项目
task test:list-projects

# 测试 rssx 项目
task test:rssx-check

# 测试 enx 项目
task test:enx-check
```

### 自定义快速测试

```bash
# 在默认项目上运行任意任务
task quick -- "你的任务描述"

# 在 rssx 项目上运行
task quick:rssx -- "列出所有配置文件"

# 在 w10n-config 项目上运行
task quick:w10n -- "检查 Ingress 配置"

# 在 enx 项目上运行
task quick:enx -- "显示项目结构"
```

**⚠️ 重要**: 选择正确的项目！
- 如果要修改 **w10n-config** 里的文件 → 用 `task quick:w10n`
- 如果要修改 **rssx** 里的文件 → 用 `task quick:rssx`
- 如果要修改 **enx** 里的文件 → 用 `task quick:enx`

**错误示例** ❌：
```bash
# 任务说"修改 w10n-config 项目中的文件"，但用了 quick:rssx
task quick:rssx -- "修改 w10n-config 项目中 rssx 的 Ingress"
# agents 会在 rssx 项目里搜索，找不到文件！
```

**正确示例** ✅：
```bash
# 文件在 w10n-config 项目里，用 quick:w10n
task quick:w10n -- "修改 rssx 的 Ingress 配置"
```

---

## 开发工作流示例

### 场景 1: 快速测试单个功能

```bash
# 1. 修改代码
vim src/agents/architect.py

# 2. 快速测试（不需要重启交互模式）
task quick:w10n -- "查看 rssx Ingress"

# 3. 继续修改
vim src/agents/developer.py

# 4. 再次测试
task test:modify-ingress
```

### 场景 2: 测试多个项目

```bash
# 测试 rssx
task quick:rssx -- "列出配置文件"

# 测试 enx
task quick:enx -- "显示项目结构"

# 测试 w10n-config
task quick:w10n -- "查看 K8s 资源"
```

### 场景 3: 调试特定问题

```bash
# 1. 运行测试，观察错误
task test:check-ingress

# 2. 修改代码
vim src/tools/file_tools.py

# 3. 立即重新测试（相同任务）
task test:check-ingress

# 4. 验证修复
task verify
```

---

## 代码质量检查

```bash
# 运行 linter
task lint

# 格式化代码
task format

# 清理临时文件
task clean
```

---

## 对比：手动 vs Task

### 手动方式（繁琐）❌

```bash
# 每次都要输入完整命令
uv run python -m src.main -p w10n-config "查看 rssx Ingress 配置"
uv run python -m src.main -p w10n-config "查看 rssx Ingress 配置"
uv run python -m src.main -p w10n-config "查看 rssx Ingress 配置"
```

### Task 方式（快捷）✅

```bash
# 简短命令，一键执行
task test:check-ingress
task test:check-ingress
task test:check-ingress
```

---

## 添加自己的测试任务

编辑 `Taskfile.yml`，添加：

```yaml
tasks:
  test:my-feature:
    desc: "测试我的新功能"
    cmds:
      - uv run python -m src.main -p rssx "测试我的功能"
```

使用：

```bash
task test:my-feature
```

---

## Shell 别名（可选）

在 `~/.zshrc` 添加：

```bash
# LangGraphX 别名
alias lgx='uv run python -m src.main'
alias lgx-rssx='uv run python -m src.main -p rssx'
alias lgx-w10n='uv run python -m src.main -p w10n-config'
alias lgx-enx='uv run python -m src.main -p enx'
```

重新加载：

```bash
source ~/.zshrc
```

使用：

```bash
lgx "列出项目"
lgx-rssx "查看配置"
lgx-w10n "检查 Ingress"
```

---

## 总结

**开发时推荐顺序**：

1. 🥇 **Task 命令** - 最快，预定义任务
2. 🥈 **命令行参数** - 灵活，自定义任务  
3. 🥉 **交互模式** - 探索性开发

**快速测试公式**：

```
修改代码 → task quick:project -- "测试" → 观察输出 → 重复
```
