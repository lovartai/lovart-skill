<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/lovart-icon.svg" />
    <source media="(prefers-color-scheme: light)" srcset="assets/lovart-icon-dark.svg" />
    <img src="assets/lovart-icon-dark.svg" width="96" height="96" alt="Lovart" />
  </picture><br/>
  <strong>lovart-skill</strong><br/><br/>
  <a href="https://github.com/lovartai/lovart-skill/releases"><img src="https://img.shields.io/github/v/release/lovartai/lovart-skill" alt="Release" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT" /></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.6+-green.svg" alt="Python 3.6+" /></a><br/>
  <a href="README.md">English</a> | <strong>简体中文</strong> | <a href="README_TW.md">繁體中文</a> | <a href="README_JA.md">日本語</a>
</p>
<br/>

> Lovart 的 AI Agent Skills — 让你常用的 AI 编程助手直接生成图片、视频和音频。一份 `SKILL.md`，两条安装路径。

## ✨ 功能

本 skill 将你的 AI 编程助手接入 Lovart Agent OpenAPI，开箱即用同时支持 [OpenClaw](https://openclaw.com) 与 [Hermes Agent](https://github.com/l3ad3r1/Hermes-skills) 两大生态；任何能调用 Python 脚本的助手同样可用。支持的能力：


- 🖼️ **图片生成** — 海报、Logo、插画、Banner、Mockup 等
- 🎬 **视频生成** — 短片、动画、产品视频
- 🎵 **音频生成** — BGM、歌曲、音效
- ✂️ **图片/视频编辑** — 超分辨率、重构图、风格迁移
- 🧊 **3D 生成** — 从文本或图片生成 3D 模型
- 📁 **项目与会话管理** — 多项目支持，本地状态持久化

## 📦 安装

根据你的 agent 生态选择对应路径。**OpenClaw 是官方发布渠道**（`npx skills add`
从 ClawHub 拉取最新 release）；**Hermes Agent 是手动拷贝到 skills 目录的安装
方式**。两条路径安装的是同一份 skill 文件，区别仅在于 agent 如何发现与调用。

无论走哪条路径，凭证都是同一组：

```bash
export LOVART_ACCESS_KEY="ak_xxx"
export LOVART_SECRET_KEY="sk_xxx"
```

在 Lovart 平台获取 AK/SK（头像菜单 -> AK/SK 管理）。

### OpenClaw

```bash
npx skills add lovartai/lovart-skill
```

拉取 ClawHub 上最新发布的 release。OpenClaw 会把 skill 装到你的项目里，并通过 `metadata.openclaw` 自动发现。

### Hermes Agent

Hermes Agent 从 `~/.hermes/skills/<category>/<skill-name>/SKILL.md` 路径发现技能。
这是**手动 / 社区安装方式** —— 本仓库目前尚无自动发布目标。

```bash
git clone https://github.com/lovartai/lovart-skill.git
cd lovart-skill
cp -r skills/lovart-skill ~/.hermes/skills/design/lovart-api
```

Hermes 通过 `metadata.hermes.tags` 在任意视觉/音频创作请求时自动触发。在 Hermes 对话框中：

```
/lovart-api 帮我画一只赛博朋克猫
```

> 💡 两条路径安装的是同一份文件——`SKILL.md` 采用双格式 frontmatter，同一份产物无需任何修改即可服务两个生态。

## 🚀 快速开始

```bash
# 生成图片
python3 scripts/agent_skill.py chat --prompt "赛博朋克风格的猫，霓虹城市背景" --json --download

# 生成视频
python3 scripts/agent_skill.py chat --prompt "海浪拍打岩石，电影感" --json --download

# 生成 BGM
python3 scripts/agent_skill.py chat --prompt "lofi hip-hop, chill, study vibes" --json --download
```

## 🛠️ 命令一览

### 生成

| 命令 | 说明 |
|------|------|
| `chat` | 发送 prompt，等待全部完成后一次性返回结果。主命令。 |
| `watch` | 发送 prompt 并流式返回 artifacts（NDJSON，生成一张交付一张） |
| `send` | 发送 prompt，不等待（立即返回 thread_id） |
| `confirm` | 确认高消耗操作（如视频生成），然后等待完成 |
| `result` | 获取会话结果 |
| `status` | 查询会话状态 |

### 项目管理

| 命令 | 说明 |
|------|------|
| `projects` | 列出所有项目 |
| `project-add` | 添加并切换到一个项目 |
| `project-switch` | 切换当前项目（支持前缀匹配） |
| `project-rename` | 重命名项目 |
| `project-remove` | 删除项目及其会话 |
| `create-project` | 在服务端创建新空项目 |

### 配置

| 命令 | 说明 |
|------|------|
| `config` | 查看/更新本地配置（`~/.lovart/state.json`） |
| `threads` | 列出保存的会话历史 |
| `set-mode` | 切换快速（消耗积分）/ 无限（排队）模式 |
| `query-mode` | 查询当前生成模式 |

### 文件操作

| 命令 | 说明 |
|------|------|
| `upload` | 上传本地文件到 CDN（返回 URL） |
| `upload-artifact` | 上传 URL 资产到项目 |
| `download` | 从 URL 下载资产 |

## 💡 使用示例

```bash
# 使用已有项目
python3 scripts/agent_skill.py chat --project-id PROJECT_ID --prompt "画一只猫" --json --download

# 继续对话（复用 thread 保留上下文）
python3 scripts/agent_skill.py chat --thread-id THREAD_ID --prompt "把背景换成蓝色" --json --download

# 流式返回（生成一张就交付一张，NDJSON 输出）
python3 scripts/agent_skill.py watch --prompt "生成 4 张赛博朋克猫的变体"

# 带参考图编辑
python3 scripts/agent_skill.py upload --file photo.jpg
python3 scripts/agent_skill.py chat --prompt "改成水彩画风格" --attachments "CDN_URL" --json --download

# 指定模型
python3 scripts/agent_skill.py chat --prompt "画一只猫" \
  --prefer-models '{"IMAGE":["generate_image_midjourney"]}' --json --download

# 强制使用特定工具（如超分而非重新生成）
python3 scripts/agent_skill.py chat --prompt "放大这张图" \
  --include-tools upscale_image --attachments "IMAGE_URL" --json --download

# Thinking 模式 — 面向复杂任务的深度结构化推理
python3 scripts/agent_skill.py chat --prompt "为咖啡品牌设计一套完整 VI" \
  --mode thinking --json --download

# 项目管理
python3 scripts/agent_skill.py projects
python3 scripts/agent_skill.py project-add --project-id NEW_ID --name "我的品牌套件"
python3 scripts/agent_skill.py project-switch --project-id NEW_ID
python3 scripts/agent_skill.py threads
```

## 🎯 模型选择

三种方式控制 Agent 使用的模型：

1. **在 prompt 中提及**（最简单）— `"用 kling 生成海浪视频"`
2. **`--prefer-models`**（软偏好）— `'{"IMAGE":["generate_image_midjourney"]}'`
3. **`--include-tools`**（硬约束）— `upscale_image`

可用模型：

<!-- AUTOGEN:models:start -->
<!-- AUTOGEN:models:end -->

## 🧠 推理模式

通过 `--mode` 控制每次请求的 agent 推理方式：

- **`fast`**（默认）— 轻量单轮响应。更快、更省，适合简单的一次性生成。
- **`thinking`** — 深度结构化推理，先规划再执行，支持多步分析。适合复杂的品牌体系、多素材活动等需要深思熟虑的任务。速度稍慢但质量更高。

```bash
# 快速单轮（默认）
python3 scripts/agent_skill.py chat --prompt "画一只猫"

# 深度推理
python3 scripts/agent_skill.py chat --prompt "设计一整套品牌识别" --mode thinking
```

**模式在 thread 首条消息时锁定**。要切换模式请开新 thread（不传 `--thread-id`）。对齐 Lovart Web UI 的模式切换。

## ⚡ 生成模式

与推理模式无关，这是账户级的持久化计费设置：

```bash
# 快速模式 — 消耗积分，无需排队
python3 scripts/agent_skill.py set-mode --fast

# 无限模式 — 免费，可能排队
python3 scripts/agent_skill.py set-mode --unlimited

# 查询当前模式
python3 scripts/agent_skill.py query-mode
```

## 🚦 频率限制

API 按接口类型分两档限流：

| 档位 | 接口 | 每分钟 | 每小时 |
|------|------|-------|-------|
| **Chat**（写接口） | `/chat`、`/chat/confirm` | 60 | 600 |
| **Query**（读接口） | `/chat/status`、`/chat/result`、`/project/*`、`/mode/*` 等其余接口 | 300 | 3000 |

更严的 Chat 档保护生成任务；Query 档宽松很多，方便轮询状态/结果不占用生成配额。

超出后返回 `HTTP 429`，响应头带 `Retry-After: 60`。

另外还有**生成并发限制**——每个 thread 同一时间只能运行一个生成任务。如果该 thread 已有任务在跑，新请求会被拒绝（返回 `HTTP 409`），需等当前任务完成。不同 thread 之间可以并行。

Skill 对网络瞬时错误会自动重试（3 次退避），但频率限制和计费错误会直接返回。

## 💾 本地状态

配置和会话历史持久化在 `~/.lovart/state.json`：

```json
{
  "active_project": "abc123...",
  "projects": {
    "abc123...": {"name": "我的项目", "created_at": "..."}
  },
  "threads": [
    {"id": "xxx", "project_id": "abc123...", "topic": "赛博朋克猫", "updated_at": "..."}
  ]
}
```

## 🤖 集成方式

本 skill 兼容多种 agent 生态，请按你的实际环境选择。

### OpenClaw

```bash
npx skills add lovartai/lovart-skill
```

OpenClaw 从 `SKILL.md` 读取 `metadata.openclaw`，安装后自动发现该 skill，除环境变量外无需额外配置。

### Hermes Agent

将 skill 放入 `~/.hermes/skills/<category>/<skill-name>/` 即可（详见上方 `安装` 一节的 Hermes 小节）。Hermes 读取 `metadata.hermes`，通过 `/lovart-api` 斜杠命令将视觉/音频创作请求路由到本 skill。

### 其他 AI 助手

同样兼容 Claude Code、Cursor 等可调用 Python 脚本的助手。完整集成协议见 `SKILL.md`。

## 📁 项目结构

```
lovart-skill/
├── README.md
├── README_CN.md
├── README_TW.md
├── README_JA.md
└── skills/
    └── lovart-skill/
        ├── SKILL.md                 # Skill 协议文件 (OpenClaw + Hermes 双格式)
        └── scripts/
            └── agent_skill.py       # Python 客户端 (零依赖)
```

## 🔒 安全与隐私

- **本地状态文件**：skill 读写 `~/.lovart/state.json` 保存当前项目和最近对话 ID，不访问其他文件
- **外部请求**：只调用 Lovart API (`https://lgw.lovart.ai`) 和 Lovart CDN（用于下载你生成的文件），不涉及第三方服务
- **API 密钥**：AK/SK 从环境变量 (`LOVART_ACCESS_KEY` / `LOVART_SECRET_KEY`) 读取，每次请求用 HMAC-SHA256 签名，密钥不会落盘也不会打印到日志
- **TLS**：**默认启用 SSL 证书校验**。仅当你在会拦截 TLS 的公司代理/VPN 环境下，可设置 `LOVART_INSECURE_SSL=1` 关闭
- **源码**：`skills/lovart-skill/scripts/agent_skill.py` 约 900 行纯 Python 标准库代码，建议安装前先通读

## 🏗️ 架构

```
用户 -> OpenClaw / Hermes Agent / Claude Code / 其他 AI 助手
         -> scripts/agent_skill.py (本 skill)
           -> Lovart OpenAPI (AK/SK HMAC-SHA256 签名认证)
             -> Lovart AI Agent (模型选择、流程编排)
               -> 生成的图片 / 视频 / 音频
```

## 🤝 贡献

欢迎贡献！你可以：

- [提交 Issue](https://github.com/lovartai/lovart-skill/issues) 反馈 bug 或建议新功能
- [提交 Pull Request](https://github.com/lovartai/lovart-skill/pulls) 修复问题或改进功能


## 📄 许可证

[MIT](LICENSE)
