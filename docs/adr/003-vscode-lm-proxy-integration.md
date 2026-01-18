# ADR-003: 使用 vscode-lm-proxy 访问 Claude Sonnet 4.5

## 状态
已接受 (2026-01-18)

## 背景

我们需要为 multi-agent 系统选择 LLM 提供商。关键约束：
- **用户只有 GitHub Copilot 订阅**（没有独立的 Anthropic/OpenAI API key）
- 需要访问 **Claude Sonnet 4.5** 模型（当前最先进的代码生成模型）
- 需要支持流式响应（streaming）以提升用户体验
- 需要本地开发环境可用

### 评估的方案

1. **直接使用 Anthropic API**
   - 需要单独购买 API key
   - 按 token 计费
   - 官方支持，稳定性高

2. **使用 OpenAI API**
   - 需要单独购买 API key
   - 按 token 计费
   - 不支持 Claude 模型

3. **vscode-lm-proxy**
   - 通过 GitHub Copilot 订阅访问多种模型
   - 无需额外 API key
   - 本地 HTTP 代理

4. **GitHub Copilot Chat API (直接)**
   - VS Code 扩展 API
   - 但不适合外部 Python 脚本调用

## 决策

**使用 vscode-lm-proxy 作为 LLM 访问桥接层**

vscode-lm-proxy 是一个 VS Code 扩展，它将 VS Code 的 Language Model API（GitHub Copilot）暴露为 OpenAI 和 Anthropic 兼容的 REST API。

## 理由

### vscode-lm-proxy 的优势

#### 1. **成本效益**
- ✅ **无需额外费用**: 使用已有的 Copilot 订阅
- ✅ 节省 API 调用费用（Claude API ~$15/1M tokens）
- ✅ 对于实验和开发阶段特别经济

#### 2. **技术兼容性**
- ✅ 提供 **Anthropic 兼容的 API**，可直接使用 `anthropic` Python SDK
- ✅ 支持流式响应（streaming）
- ✅ 支持消息格式转换（自动处理）
- ✅ 可访问 Claude Sonnet 4.5 等最新模型

#### 3. **集成简单**
```python
from anthropic import Anthropic

# 只需修改 base_url 即可
client = Anthropic(
    api_key='dummy',  # proxy 不验证 key
    base_url='http://localhost:4000/anthropic'
)

# 其余代码与官方 SDK 完全相同
message = client.messages.create(
    model='claude-sonnet-4.5',
    max_tokens=1024,
    messages=[{'role': 'user', 'content': 'Hello!'}]
)
```

#### 4. **开发体验**
- ✅ 本地运行，低延迟
- ✅ VS Code 集成，状态栏显示服务器状态
- ✅ 可配置日志级别便于调试
- ✅ 支持多种模型选择

#### 5. **可移植性**
- ✅ 代码与官方 Anthropic SDK 兼容
- ✅ 未来迁移到官方 API 只需修改 `base_url`
- ✅ 可以在本地和云端之间轻松切换

### 架构

```
┌─────────────────────┐
│  LangGraph Agents   │
│   (Python code)     │
└──────────┬──────────┘
           │ HTTP Request
           │ (Anthropic format)
           ▼
┌─────────────────────┐
│  vscode-lm-proxy    │
│  (VS Code Extension)│
│  Port: 4000         │
└──────────┬──────────┘
           │ VS Code LM API
           ▼
┌─────────────────────┐
│  GitHub Copilot     │
│  (Subscription)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Claude Sonnet 4.5  │
│  (via Copilot)      │
└─────────────────────┘
```

### vscode-lm-proxy 技术细节

**安装配置**:
```json
// VS Code settings.json
{
  "vscode-lm-proxy.port": 4000,
  "vscode-lm-proxy.logLevel": 1,  // INFO
  "vscode-lm-proxy.showOutputOnStartup": false
}
```

**API 端点**:
- `POST /anthropic/v1/messages` - 创建消息（支持 streaming）
- `GET /anthropic/v1/models` - 列出可用模型
- `POST /anthropic/v1/messages/count_tokens` - Token 计数

**支持的模型**（通过 Copilot）:
- `claude-sonnet-4.5` - 最新 Claude 模型
- `gpt-4o` - OpenAI GPT-4 Optimized
- 其他 Copilot 支持的模型

**流式响应示例**:
```python
with client.messages.stream(
    model='claude-sonnet-4.5',
    max_tokens=1024,
    messages=[{'role': 'user', 'content': 'Write code'}]
) as stream:
    for text in stream.text_stream:
        print(text, end='', flush=True)
```

## 结果

### 正面影响

1. **成本节省**
   - 开发阶段无额外 LLM 费用
   - 可以大量测试和迭代

2. **开发效率**
   - 与 Anthropic SDK 完全兼容
   - 本地部署，响应快速
   - 易于调试

3. **灵活性**
   - 代码可移植到官方 API
   - 支持多种模型选择
   - 可以根据任务选择不同模型

### 负面影响

1. **依赖 VS Code 环境**
   - ⚠️ 必须在 VS Code 中运行
   - ⚠️ 需要 GitHub Copilot 订阅激活
   - ⚠️ 不适合生产部署（仅限开发）

2. **潜在的稳定性风险**
   - ⚠️ 第三方扩展，非官方支持
   - ⚠️ 可能受 VS Code/Copilot API 变化影响
   - ⚠️ 限流和配额由 Copilot 控制

3. **功能限制**
   - ⚠️ 依赖 Copilot 支持的模型
   - ⚠️ 可能有请求频率限制
   - ⚠️ 无法使用官方 API 的所有高级特性

### 风险和缓解

**风险1: vscode-lm-proxy 停止维护**
- **可能性**: 中等
- **影响**: 高
- **缓解**: 
  - 代码设计与 Anthropic SDK 兼容，迁移成本低
  - 准备官方 API 的迁移方案
  - 关注项目 GitHub 动态

**风险2: Copilot 限流导致服务中断**
- **可能性**: 低
- **影响**: 中等
- **缓解**:
  - 实现请求重试机制
  - 添加速率限制（rate limiting）
  - 监控请求失败率

**风险3: 响应质量或延迟问题**
- **可能性**: 低
- **影响**: 中等
- **缓解**:
  - 测试阶段充分评估
  - 实现超时和降级机制
  - 准备切换到官方 API

**风险4: 无法用于生产环境**
- **可能性**: 确定
- **影响**: 中等（如果需要部署）
- **缓解**:
  - 明确定位为**开发和测试工具**
  - 生产环境规划使用官方 API
  - 设计抽象层便于切换

## 实现要点

### 1. LLM 客户端抽象

创建抽象层以便未来切换：

```python
# src/llm/client.py
from abc import ABC, abstractmethod

class LLMClient(ABC):
    @abstractmethod
    def create_message(self, messages, **kwargs):
        pass

class ProxyLLMClient(LLMClient):
    """使用 vscode-lm-proxy"""
    def __init__(self):
        self.client = Anthropic(
            api_key='dummy',
            base_url='http://localhost:4000/anthropic'
        )
    
    def create_message(self, messages, **kwargs):
        return self.client.messages.create(
            messages=messages, **kwargs
        )

class OfficialLLMClient(LLMClient):
    """使用官方 Anthropic API（未来）"""
    def __init__(self, api_key):
        self.client = Anthropic(api_key=api_key)
    
    def create_message(self, messages, **kwargs):
        return self.client.messages.create(
            messages=messages, **kwargs
        )
```

### 2. 配置管理

```python
# config.yaml
llm:
  provider: vscode-lm-proxy  # or 'anthropic-official'
  proxy:
    base_url: http://localhost:4000/anthropic
    port: 4000
  model: claude-sonnet-4.5
  max_tokens: 4096
  temperature: 0.7
```

### 3. 健康检查

```python
def check_proxy_health():
    """检查 vscode-lm-proxy 是否运行"""
    try:
        response = requests.get(
            'http://localhost:4000/anthropic/v1/models',
            timeout=2
        )
        return response.status_code == 200
    except:
        return False
```

## 迁移路径

### 阶段 1: 开发阶段（当前）
- 使用 vscode-lm-proxy
- 充分测试和验证
- 评估性能和稳定性

### 阶段 2: 评估阶段（3-6个月）
- 收集使用数据（延迟、失败率、成本）
- 评估是否需要迁移到官方 API
- 如果 vscode-lm-proxy 足够稳定，可继续使用

### 阶段 3: 生产准备（如需要）
- 申请 Anthropic 官方 API key
- 修改配置切换到官方 API
- 代码无需修改（已抽象）

## 成功指标

跟踪以下指标验证决策：
- **可用性**: 目标 >95% uptime
- **延迟**: 目标 <2s 首 token，<5s 完整响应
- **成功率**: 目标 >98% 请求成功
- **成本**: $0（使用 Copilot 订阅）

## 前置条件

使用 vscode-lm-proxy 需要：
1. ✅ VS Code 1.101.0+
2. ✅ 活跃的 GitHub Copilot 订阅
3. ✅ 安装 vscode-lm-proxy 扩展
4. ✅ 启动 proxy 服务器（通过命令面板）

## 参考资料

- [vscode-lm-proxy GitHub](https://github.com/ryonakae/vscode-lm-proxy)
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)
- [VS Code Language Model API](https://code.visualstudio.com/api/extension-guides/language-model)

## 备注

此决策可能在以下情况下重新评估：
- vscode-lm-proxy 出现重大问题或停止维护
- GitHub Copilot 政策变化，禁止此类使用
- 需要部署到生产环境
- 需要使用官方 API 独有的高级特性
- 成本不再是主要考虑因素
