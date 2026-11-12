# AI 智能伴侣（AI Companion）

一个基于 **Streamlit + DeepSeek 大模型**的网页版 AI 伴侣应用：可以给伴侣起昵称、设定性格，像微信聊天一样短句对话，回复流式逐字输出，会话自动保存到本地并可随时新建、切换、删除。

> 说明：本仓库包含「AI 智能伴侣」多个逐步迭代版本的实现，`app.py → app1.py → app2.py → app3.py` 是逐步迭代的四个版本，`实例.py` 是整理后的参考实现。各版本差异见[版本对照](#版本对照)。

---

## 1. 项目解决什么问题

| 真实痛点 | 本项目的做法 |
| --- | --- |
| 通用 AI 助手回答冗长、爱写"场景描写/心理活动"，不像真人聊天 | 用固定 system prompt 约束输出：**每次只回 1 条消息、禁止场景或状态描述性文字、回复简短像微信聊天、匹配用户语言、可发表情** |
| 每次对话都要重新交代"你叫什么、什么性格" | 侧边栏一次设置**昵称 + 性格**，每次请求自动拼进 system prompt（`%s` 占位符注入） |
| 回复要等整段生成完才出现，等待感强 | 用 `stream=True` + `st.empty()` 占位，**逐字流式渲染**回复 |
| 关掉页面聊天记录就没了，也无法同时经营多段关系 | 会话以 **JSON 文件**保存在 `sessions/` 目录，支持新建、历史会话切换、删除 |
| 单文件 Demo 无法演进、不好讲解 | 拆成 4 个渐进版本 + 1 个重构参考版，便于对照学习每一步加了什么 |

---

## 2. 主要功能

### 核心功能

- **流式对话聊天**：基于 `st.chat_input` + `st.chat_message`，用户消息与 AI 回复以气泡形式呈现；回复通过 `stream=True` 逐字追加显示，而不是等整段返回。
- **伴侣人设自定义**：侧边栏「伴侣信息」中可修改
  - 昵称（`st.text_input`），默认 `小怡`（`实例.py` 为 `小甜甜`）
  - 性格（`st.text_area`），默认 `活泼开朗的河南姑娘`（`实例.py` 为 `活泼开朗的东北姑娘`）
  - 修改后的昵称与性格会即时写入 `st.session_state`，并在下一次请求时生效。
- **角色扮演系统提示词**：内置 7 条规则（只回 1 条消息、禁止场景描述、匹配语言、简短、符合性格、可发表情等），使模型"完全代入伴侣角色"。
- **多会话管理**（`app2.py` 起）
  - 新建会话：先保存当前会话，再清空消息并生成新会话标识，然后 `st.rerun()`
  - 历史会话：侧边栏列出 `sessions/` 下的会话按钮，点击即加载该会话的消息、昵称、性格；当前会话按钮高亮为 `primary`
  - 删除会话：删除对应 JSON 文件；若删除的是当前会话，则清空消息并换新会话标识（`app3.py`、`实例.py` 可用）
- **本地持久化**：会话写入 `sessions/<会话标识>.json`，`ensure_ascii=False` 保留中文可读；目录不存在时自动创建。
- **DeepSeek 接入**：`openai` SDK 指向 `https://api.deepseek.com`，密钥从环境变量 `DEEPSEEK_API_KEY` 读取。
- **思考模式参数**：`app.py`~`app3.py` 请求时传入 `reasoning_effort="high"` 与 `extra_body={"thinking": {"type": "enabled"}}`，用于请求模型输出思考过程（`实例.py` 未传这些参数）。实际是否返回思考内容取决于所调用的模型与接口。
- **页面配置**：标题「AI伴侣」、图标 🎡（`实例.py` 为「AI智能伴侣」+ 🤖）、`layout="wide"` 宽屏、侧边栏默认展开。

### 版本对照

| 文件 | 人设设置 | 会话保存 | 历史切换 | 删除会话 | 模型与参数 | 可运行性 |
| --- | --- | --- | --- | --- | --- | --- |
| `app.py` | ✗（固定"温柔知心的小怡"） | ✗ | ✗ | ✗ | `deepseek-flash`，流式 + 思考模式 | ✅ |
| `app1.py` | ✅ 昵称 + 性格 | ✗ | ✗ | ✗ | 同上 | ✅ |
| `app2.py` | ✅ | ✅ | ✅ | ✗（按钮为占位 `pass`） | 同上 | ✅ |
| `app3.py` | ✅ | ✅ | ✅ | ✅ | 同上 | ✅ ← **推荐入口** |
| `实例.py` | ✅ | ✅ | ✅（按时间倒序） | ✅ | `deepseek-chat`，仅流式 | ⚠️ 需先补 `resources/logo.png`，见[已知限制](#6-注意事项与已知限制) |

---

## 3. 安装方法

### 3.1 环境要求

- Python **3.11**（已在 `3.11.9` 下验证通过）
- 一个可用的 **DeepSeek API Key**（[platform.deepseek.com](https://platform.deepseek.com/) 申请）
- 依赖库（已在 `.venv` 中实测的版本）：
  - `streamlit==1.66.1`
  - `openai==3.44.0`

### 3.2 安装步骤

```powershell
# 1. 进入项目目录（替换为你本地的实际路径）
cd 你的项目目录

# 2. 创建并激活虚拟环境（如本地已创建过 .venv，可跳过此项）
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. 安装依赖（仓库未提供 requirements.txt，直接安装）
pip install streamlit openai
```

> 如需锁定版本：`pip install streamlit==1.66.1 openai==3.44.0`

### 3.3 配置 API Key

程序从环境变量 `DEEPSEEK_API_KEY` 读取密钥，**必须先设置再启动**：

```powershell
# 当前 PowerShell 会话（临时）
$env:DEEPSEEK_API_KEY = "sk-你的密钥"

# 永久写入用户环境变量（新开终端生效）
setx DEEPSEEK_API_KEY "sk-你的密钥"
```

```cmd
:: CMD
set DEEPSEEK_API_KEY=sk-你的密钥
```

```bash
# macOS / Linux
export DEEPSEEK_API_KEY="sk-你的密钥"
```

> ⚠️ 未设置 `DEEPSEEK_API_KEY` 时，`OpenAI(api_key=None, ...)` 会在脚本开头直接抛出 `OpenAIError: Missing credentials`，页面无法加载。
> 另外，`api_key` 为 `None` 时 SDK 会回退使用 `OPENAI_API_KEY`——若你只设置了 `OPENAI_API_KEY`，程序会拿 OpenAI 的密钥去请求 DeepSeek 接口，通常得到鉴权失败。

---

## 4. 使用方法

### 4.1 启动

```powershell
# 推荐运行最完整且开箱即用的 app3.py
.\.venv\Scripts\python.exe -m streamlit run app3.py

# 或直接使用 streamlit 命令
streamlit run app3.py
```

浏览器会自动打开（默认 `http://localhost:8501`）。若想指定端口：

```powershell
streamlit run app3.py --server.port 8599
```

### 4.2 界面操作

1. **设置伴侣**：左侧边栏「伴侣信息」中填写昵称、性格（例如"活泼开朗的河南姑娘"），下一次发送即按新人设回复。
2. **开始聊天**：底部输入框输入内容并回车，回复会逐字流式出现；聊天记录在当前页面持续保留。
3. **新建会话**：点击侧边栏「新建会话」✏️/🚀，当前会话先保存，然后清空对话、生成新的会话标识（按秒级时间戳命名）。
4. **切换历史会话**：侧边栏「会话历史」列出 `sessions/` 下的会话，点击文件名即加载该会话的聊天记录与人设；当前会话按钮为高亮状态。
5. **删除会话**：点击会话右侧的 ❌，删除对应 JSON 文件（`app3.py` / `实例.py` 生效）。

### 4.3 会话文件说明

每收到一条 AI 回复后自动保存（新建会话时也会先保存当前会话），路径为 `sessions/<YYYY-MM-DD-HH-MM-SS>.json`。

`app2.py` / `app3.py` 的格式（首次对话后自动生成，格式如下）：

```json
{
  "name": "小怡",
  "character": "活泼开朗的河南姑娘",
  "messages": [
    { "role": "user", "content": "你好" },
    { "role": "assistant", "content": "哎哟，你可算来啦！等你好久啦～😊" }
  ],
  "session_id": "2026-11-11-19-37-21"
}
```

`实例.py` 使用另一套字段名：`nick_name` / `nature` / `current_session` / `messages`。

> ⚠️ 两种格式**不通用**：用 `实例.py` 加载 `app2.py`/`app3.py` 写出的会话文件会因缺少 `nick_name` 字段而提示「加载会话失败!」。切换入口脚本时建议先用同一份脚本新建会话。

---

## 5. 项目结构

```text
python.project/
├── app.py              # v1 最小可用：固定人设 + 流式对话 + 思考模式
├── app1.py             # v2 增加侧边栏昵称/性格自定义
├── app2.py             # v3 增加会话保存/历史切换（删除按钮为占位）
├── app3.py             # v4 增加删除会话 —— 推荐运行入口
├── 实例.py              # 重构参考版：函数化、日志、emoji 性格、会话倒序、st.logo
├── main.py             # PyCharm 默认示例脚本，与伴侣功能无关
├── 文件操作入门.py      # Python 文件读写练习，与伴侣功能无关
├── 演示.txt / 演示1.txt # 文件读写练习用的文本素材
├── .gitignore          # 忽略规则：虚拟环境、会话数据、IDE 配置、缓存
├── sessions/           # 会话持久化目录（JSON，首次对话时自动创建）
├── .venv/              # Python 虚拟环境（本机安装，不入库）
└── .idea/              # PyCharm 工程配置（本机安装，不入库）
```

> 仓库已配置 [.gitignore](.gitignore)：`.venv/`、`sessions/`（聊天记录）、`.idea/`、`__pycache__/` 与练习生成的 `演示1.txt` 都不会进入版本库。

---

## 6. 注意事项与已知限制

1. **`实例.py` 缺少 logo 素材**：该脚本第 83 行调用 `st.logo("resources/logo.png")`，但仓库中**没有 `resources/` 目录**，直接运行会抛出 `StreamlitAPIException: The image passed to st.logo is invalid` 并中断。使用前请：
   - 新建 `resources/` 目录并放入 `logo.png`；或
   - 注释/删除 `st.logo("resources/logo.png")` 这一行。
2. **`app2.py` 的删除按钮未实现**：右侧 ❌ 的回调是 `pass`，点击不会删除任何文件；删除功能从 `app3.py` 起才可用。
3. **`app3.py` 的删除按钮不会立即刷新列表**：`delete_session()` 没有返回值，`if delete_session(session): st.rerun()` 因此不会触发重跑，被删项要等下一次交互（再次点击）才从侧边栏消失；文件本身已删除。`实例.py` 中该处为无条件 `st.rerun()`，行为正常。
4. **`app.py` / `app1.py` 的历史消息只在发送新消息时回显**：消息遍历写在 `if prompt:` 分支内，页面重跑但未发消息时看不到旧记录（数据仍在 `st.session_state` 中）。
5. **会话标识按秒生成**：同一秒内连续新建会话可能重名。
6. **会话数据为本地明文 JSON**：无加密、无多用户隔离，不要存放敏感信息。
7. **无 `requirements.txt`、无测试**：依赖版本以本文档「3.1 环境要求」为准。
8. **顶部文案**：`app2.py`/`app3.py` 顶部 `st.text(f"会话名称: {name}")` 实际显示的是**伴侣昵称**，而 `实例.py` 显示的是会话 ID。

---

## 7. 技术栈与已验证环境

| 项目 | 版本 / 说明 |
| --- | --- |
| Python | 3.11.9 |
| Streamlit | 1.66.1 |
| OpenAI SDK | 3.44.0 |
| 模型 | `deepseek-flash`（`app.py`~`app3.py`）、`deepseek-chat`（`实例.py`） |
| 接口地址 | `https://api.deepseek.com` |
| 密钥变量 | `DEEPSEEK_API_KEY` |

验证记录（使用 Streamlit 官方 `streamlit.testing.v1.AppTest` 脚本化执行）：

- `app.py`、`app1.py`、`app2.py`、`app3.py` 首屏渲染均无异常；
- `app3.py` 的历史会话加载可用（点击会话按钮后成功恢复 2 条消息与昵称）；
- `实例.py` 首屏即因 `resources/logo.png` 缺失报错（见[已知限制](#6-注意事项与已知限制)第 1 条）。

---

## 8. 许可证

本项目采用 [MIT License](LICENSE) 开源：可自由使用、修改、分发与商用，保留版权声明与许可声明即可。

如需把版权所有者改成个人或组织名称，请编辑 [LICENSE](LICENSE) 中 `Copyright (c) 2026 ...` 这一行的署名部分。
