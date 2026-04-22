<!-- 本檔案由 templates/README_TW.md 自動生成，請勿直接修改根目錄檔案；修改範本後 CI 會重新生成。 -->

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
  <a href="README.md">English</a> | <a href="README_CN.md">简体中文</a> | <strong>繁體中文</strong> | <a href="README_JA.md">日本語</a>
</p>
<br/>

> [Lovart](https://lovart.ai) 的 AI Agent Skills — 讓你的 AI 程式設計助手輕鬆生成圖片、影片和音訊。

## ✨ 功能

將 [OpenClaw](https://openclaw.com)（及其他 AI 程式設計助手）連接到 Lovart Agent OpenAPI：

- 🖼️ **圖片生成** — 海報、Logo、插畫、Banner、Mockup 等
- 🎬 **影片生成** — 短片、動畫、產品影片
- 🎵 **音訊生成** — BGM、歌曲、音效
- ✂️ **圖片/影片編輯** — 超解析度、重構圖、風格轉換
- 🧊 **3D 生成** — 從文字或圖片生成 3D 模型
- 📁 **專案與對話管理** — 多專案支援，本地狀態持久化

## 📦 安裝

```bash
npx skills add lovartai/lovart-skill
```

然後設定環境變數：

```bash
export LOVART_ACCESS_KEY="ak_xxx"
export LOVART_SECRET_KEY="sk_xxx"
```

在 Lovart 平台取得 AK/SK（頭像選單 -> AK/SK 管理）。

> 🎉 **就這麼簡單！** Skill 檔案會被新增到你的專案中，AI Agent 將自動偵測並呼叫，無需手動執行任何腳本。

## 🚀 快速開始

```bash
# 生成圖片
python3 agent_skill.py chat --prompt "賽博龐克風格的貓，霓虹城市背景" --json --download

# 生成影片
python3 agent_skill.py chat --prompt "海浪拍打岩石，電影感" --json --download

# 生成 BGM
python3 agent_skill.py chat --prompt "lofi hip-hop, chill, study vibes" --json --download
```

## 🛠️ 指令一覽

### 生成

| 指令 | 說明 |
|------|------|
| `chat` | 傳送 prompt，等待全部完成後一次回傳結果。主指令。 |
| `watch` | 傳送 prompt 並串流回傳 artifacts（NDJSON，完成一張交付一張） |
| `send` | 傳送 prompt，不等待（立即回傳 thread_id） |
| `confirm` | 確認高消耗操作（如影片生成），然後等待完成 |
| `result` | 取得對話結果 |
| `status` | 查詢對話狀態 |

### 專案管理

| 指令 | 說明 |
|------|------|
| `projects` | 列出所有專案 |
| `project-add` | 新增並切換至一個專案 |
| `project-switch` | 切換目前專案（支援前綴匹配） |
| `project-rename` | 重新命名專案 |
| `project-remove` | 刪除專案及其對話 |
| `create-project` | 在伺服器端建立新空專案 |

### 設定

| 指令 | 說明 |
|------|------|
| `config` | 檢視/更新本地設定（`~/.lovart/state.json`） |
| `threads` | 列出已儲存的對話歷史 |
| `set-mode` | 切換快速（消耗點數）/ 無限（排隊）模式 |
| `query-mode` | 查詢目前生成模式 |

### 檔案操作

| 指令 | 說明 |
|------|------|
| `upload` | 上傳本地檔案到 CDN（回傳 URL） |
| `upload-artifact` | 上傳 URL 資產到專案 |
| `download` | 從 URL 下載資產 |

## 💡 使用範例

```bash
# 使用既有專案
python3 agent_skill.py chat --project-id PROJECT_ID --prompt "畫一隻貓" --json --download

# 繼續對話（重用 thread 保留上下文）
python3 agent_skill.py chat --thread-id THREAD_ID --prompt "把背景換成藍色" --json --download

# 串流回傳（完成一張就交付一張，NDJSON 輸出）
python3 agent_skill.py watch --prompt "生成 4 張賽博龐克貓的變體"

# 帶參考圖編輯
python3 agent_skill.py upload --file photo.jpg
python3 agent_skill.py chat --prompt "改成水彩畫風格" --attachments "CDN_URL" --json --download

# 指定模型
python3 agent_skill.py chat --prompt "畫一隻貓" \
  --prefer-models '{"IMAGE":["generate_image_midjourney"]}' --json --download

# 強制使用特定工具（如超解析度而非重新生成）
python3 agent_skill.py chat --prompt "放大這張圖" \
  --include-tools upscale_image --attachments "IMAGE_URL" --json --download

# Thinking 模式 — 面向複雜任務的深度結構化推理
python3 agent_skill.py chat --prompt "為咖啡品牌設計一套完整 VI" \
  --mode thinking --json --download

# 專案管理
python3 agent_skill.py projects
python3 agent_skill.py project-add --project-id NEW_ID --name "我的品牌套件"
python3 agent_skill.py project-switch --project-id NEW_ID
python3 agent_skill.py threads
```

## 🎯 模型選擇

三種方式控制 Agent 使用的模型：

1. **在 prompt 中提及**（最簡單）— `"用 kling 生成海浪影片"`
2. **`--prefer-models`**（軟偏好）— `'{"IMAGE":["generate_image_midjourney"]}'`
3. **`--include-tools`**（硬約束）— `upscale_image`

可用模型：

| 類別 | Tool name | 顯示名 | 會員專屬 |
|---|---|---|---|
| 圖片 | `generate_image_flux_2_max` | Flux.2 Max |  |
| 圖片 | `generate_image_flux_2_pro` | Flux.2 Pro |  |
| 圖片 | `generate_image_gpt_image_1_5` | GPT Image 1.5 |  |
| 圖片 | `generate_image_gpt_image_2` | GPT Image 2 Auto |  |
| 圖片 | `generate_image_gpt_image_2_high` | GPT Image 2 High |  |
| 圖片 | `generate_image_gpt_image_2_low` | GPT Image 2 Low |  |
| 圖片 | `generate_image_gpt_image_2_medium` | GPT Image 2 Medium |  |
| 圖片 | `generate_image_imagen_v4` | Gemini Imagen 4 |  |
| 圖片 | `generate_image_midjourney` | Midjourney |  |
| 圖片 | `generate_image_nano_banana` | Nano Banana |  |
| 圖片 | `generate_image_nano_banana_2` | Nano Banana 2 |  |
| 圖片 | `generate_image_nano_banana_pro` | Nano Banana Pro |  |
| 圖片 | `generate_image_seedream_v4` | Seedream 4 |  |
| 圖片 | `generate_image_seedream_v4_5` | Seedream 4.5 |  |
| 圖片 | `generate_image_seedream_v5` | Seedream 5.0 Lite |  |
| 影片 | `generate_video_hailuo_v2_3` | Hailuo 2.3 |  |
| 影片 | `generate_video_kling_omni_v1` | Kling O1 | ⭐ |
| 影片 | `generate_video_kling_v2_6` | Kling 2.6 | ⭐ |
| 影片 | `generate_video_kling_v3` | Kling 3.0 | ⭐ |
| 影片 | `generate_video_kling_v3_omni` | Kling 3.0 Omni | ⭐ |
| 影片 | `generate_video_seedance_pro_v1_5` | Seedance 1.5 Pro |  |
| 影片 | `generate_video_seedance_v2_0` | Seedance 2.0 | ⭐ |
| 影片 | `generate_video_seedance_v2_0_fast` | Seedance 2.0 Fast | ⭐ |
| 影片 | `generate_video_sora_v2` | Sora 2 | ⭐ |
| 影片 | `generate_video_sora_v2_pro` | Sora 2 Pro | ⭐ |
| 影片 | `generate_video_veo3` | Veo 3 | ⭐ |
| 影片 | `generate_video_veo3_1` | Veo 3.1 | ⭐ |
| 影片 | `generate_video_veo3_1_fast` | Veo 3.1 Fast | ⭐ |
| 影片 | `generate_video_vidu_q2` | Vidu Q2 |  |
| 影片 | `generate_video_wan_v2_6` | Wan 2.6 |  |
| 3D | `generate_3d_tripo` | Tripo |  |

## 🧠 推理模式

透過 `--mode` 控制每次請求的 agent 推理方式：

- **`fast`**（預設）— 輕量單輪回應。較快、較省，適合簡單的一次性生成。
- **`thinking`** — 深度結構化推理，先規劃再執行，支援多步分析。適合複雜的品牌體系、多素材活動等需要深思熟慮的任務。速度稍慢但品質更高。

```bash
# 快速單輪（預設）
python3 agent_skill.py chat --prompt "畫一隻貓"

# 深度推理
python3 agent_skill.py chat --prompt "設計一整套品牌識別" --mode thinking
```

**模式在 thread 首條訊息時鎖定**。要切換模式請開新 thread（不傳 `--thread-id`）。對齊 Lovart Web UI 的模式切換。

## ⚡ 生成模式

與推理模式無關，這是帳戶級的持久化計費設定：

```bash
# 快速模式 — 消耗點數，無需排隊
python3 agent_skill.py set-mode --fast

# 無限模式 — 免費，可能排隊
python3 agent_skill.py set-mode --unlimited

# 查詢目前模式
python3 agent_skill.py query-mode
```

## 🚦 頻率限制

API 依介面類型分兩檔限流：

| 檔位 | 介面 | 每分鐘 | 每小時 |
|------|------|-------|-------|
| **Chat**（寫介面） | `/chat`、`/chat/confirm` | 60 | 600 |
| **Query**（讀介面） | `/chat/status`、`/chat/result`、`/project/*`、`/mode/*` 等其餘介面 | 300 | 3000 |

較嚴的 Chat 檔保護生成任務；Query 檔寬鬆很多，方便輪詢狀態/結果不占用生成配額。

超出後回傳 `HTTP 429`，回應頭帶 `Retry-After: 60`。

另外還有**生成並行限制**——每個 thread 同一時間只能執行一個生成任務。如果該 thread 已有任務在跑，新請求會被拒絕（回傳 `HTTP 409`），需等當前任務完成。不同 thread 之間可以並行。

Skill 對網路瞬時錯誤會自動重試（3 次退避），但頻率限制和計費錯誤會直接回傳。

## 💾 本地狀態

設定和對話歷史持久化在 `~/.lovart/state.json`：

```json
{
  "active_project": "abc123...",
  "projects": {
    "abc123...": {"name": "我的專案", "created_at": "..."}
  },
  "threads": [
    {"id": "xxx", "project_id": "abc123...", "topic": "賽博龐克貓", "updated_at": "..."}
  ]
}
```

## 🤖 整合方式

### OpenClaw（推薦）

```bash
npx skills add lovartai/lovart-skill
```

本 skill 為 [OpenClaw](https://openclaw.com) 一等公民 skill。安裝後 AI Agent 會自動偵測並呼叫，除環境變數外無需額外設定。

### 其他 AI 助手

同樣相容 Claude Code、Cursor 等可呼叫 Python 腳本的助手。完整整合協議見 `SKILL.md`。

## 📁 專案結構

```
lovart-skill/
├── README.md
├── README_CN.md
├── README_TW.md
├── README_JA.md
└── skills/
    └── lovart-skill/
        ├── SKILL.md          # Skill 協議檔案 (OpenClaw 規範)
        └── agent_skill.py    # Python 客戶端 (零依賴)
```

## 🔒 安全與隱私

- **本地狀態檔案**：skill 讀寫 `~/.lovart/state.json` 保存目前專案和近期對話 ID，不存取其他檔案
- **外部請求**：只呼叫 Lovart API (`https://lgw.lovart.ai`) 和 Lovart CDN（用於下載你產生的檔案），不涉及第三方服務
- **API 金鑰**：AK/SK 從環境變數 (`LOVART_ACCESS_KEY` / `LOVART_SECRET_KEY`) 讀取，每次請求以 HMAC-SHA256 簽章，金鑰不會落盤也不會印到日誌
- **TLS**：**預設啟用 SSL 憑證驗證**。僅當你在會攔截 TLS 的公司代理/VPN 環境下，可設定 `LOVART_INSECURE_SSL=1` 關閉
- **原始碼**：`skills/lovart-skill/agent_skill.py` 約 900 行純 Python 標準函式庫程式碼，建議安裝前先通讀

## 🏗️ 架構

```
使用者 -> OpenClaw / Claude Code / 其他 AI 助手
            -> agent_skill.py (本 skill)
              -> Lovart OpenAPI (AK/SK HMAC-SHA256 簽章認證)
                -> Lovart AI Agent (模型選擇、流程編排)
                  -> 生成的圖片 / 影片 / 音訊
```

## 🤝 貢獻

歡迎貢獻！你可以：

- [提交 Issue](https://github.com/lovartai/lovart-skill/issues) 回報 bug 或建議新功能
- [提交 Pull Request](https://github.com/lovartai/lovart-skill/pulls) 修復問題或改進功能


## 📄 授權條款

[MIT](LICENSE)
