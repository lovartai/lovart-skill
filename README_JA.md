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
  <a href="README.md">English</a> | <a href="README_CN.md">简体中文</a> | <a href="README_TW.md">繁體中文</a> | <strong>日本語</strong>
</p>
<br/>

> [Lovart](https://lovart.ai) の AI Agent Skills — AI コーディングアシスタントから画像・動画・音声を簡単に生成。

## ✨ 機能

[OpenClaw](https://openclaw.com)（およびその他の AI コーディングアシスタント）を Lovart Agent OpenAPI に接続します：

- 🖼️ **画像生成** — ポスター、ロゴ、イラスト、バナー、モックアップなど
- 🎬 **動画生成** — ショートクリップ、アニメーション、プロダクトビデオ
- 🎵 **音声生成** — BGM、楽曲、効果音
- ✂️ **画像/動画編集** — 超解像、リフレーム、スタイル変換
- 🧊 **3D 生成** — テキストや画像から 3D モデルを生成
- 📁 **プロジェクト・スレッド管理** — マルチプロジェクト対応、ローカル状態の永続化

## 📦 インストール

```bash
npx skills add lovartai/lovart-skill
```

環境変数を設定します：

```bash
export LOVART_ACCESS_KEY="ak_xxx"
export LOVART_SECRET_KEY="sk_xxx"
```

Lovart プラットフォームで AK/SK を取得してください（アバターメニュー -> AK/SK 管理）。

> 🎉 **これだけです！** Skill ファイルがプロジェクトに追加され、AI Agent が自動検出して呼び出します。スクリプトを手動で実行する必要はありません。

## 🚀 クイックスタート

```bash
# 画像生成
python3 agent_skill.py chat --prompt "サイバーパンクな猫、ネオンシティの背景" --json --download

# 動画生成
python3 agent_skill.py chat --prompt "岩に打ち寄せる波、シネマティック" --json --download

# BGM 生成
python3 agent_skill.py chat --prompt "lofi hip-hop, chill, study vibes" --json --download
```

## 🛠️ コマンド一覧

### 生成

| コマンド | 説明 |
|----------|------|
| `chat` | プロンプトを送信し、全完了後に一括で結果を返す。メインコマンド。 |
| `watch` | プロンプトを送信し artifacts を完了次第ストリーミング返却（NDJSON） |
| `send` | プロンプトを送信、待機なし（thread_id を即座に返す） |
| `confirm` | 高コスト操作（例：動画生成）を確認し、完了を待つ |
| `result` | スレッドの結果を取得 |
| `status` | スレッドの状態を確認 |

### プロジェクト管理

| コマンド | 説明 |
|----------|------|
| `projects` | 全プロジェクトを一覧表示 |
| `project-add` | プロジェクトを追加して切り替え |
| `project-switch` | アクティブプロジェクトを切り替え（プレフィックスマッチ対応） |
| `project-rename` | プロジェクト名を変更 |
| `project-remove` | プロジェクトとそのスレッドを削除 |
| `create-project` | サーバー上に新しい空プロジェクトを作成 |

### 設定

| コマンド | 説明 |
|----------|------|
| `config` | ローカル設定の表示/更新（`~/.lovart/state.json`） |
| `threads` | 保存済みの会話スレッドを一覧表示 |
| `set-mode` | 高速（クレジット消費）/ 無制限（キュー）モードを切り替え |
| `query-mode` | 現在の生成モードを確認 |

### ファイル操作

| コマンド | 説明 |
|----------|------|
| `upload` | ローカルファイルを CDN にアップロード（URL を返す） |
| `upload-artifact` | URL アーティファクトをプロジェクトにアップロード |
| `download` | URL からアーティファクトをダウンロード |

## 💡 使用例

```bash
# 既存プロジェクトを使用
python3 agent_skill.py chat --project-id PROJECT_ID --prompt "猫を描いて" --json --download

# 会話を継続（スレッド再利用でコンテキストを保持）
python3 agent_skill.py chat --thread-id THREAD_ID --prompt "背景を青にして" --json --download

# ストリーミング返却（完成次第 1 枚ずつ配信、NDJSON 出力）
python3 agent_skill.py watch --prompt "サイバーパンクな猫のバリエーションを 4 枚"

# 参考画像付きで編集
python3 agent_skill.py upload --file photo.jpg
python3 agent_skill.py chat --prompt "水彩画風に変えて" --attachments "CDN_URL" --json --download

# モデルを指定
python3 agent_skill.py chat --prompt "猫を描いて" \
  --prefer-models '{"IMAGE":["generate_image_midjourney"]}' --json --download

# 特定ツールを強制使用（再生成ではなく超解像）
python3 agent_skill.py chat --prompt "この画像を拡大して" \
  --include-tools upscale_image --attachments "IMAGE_URL" --json --download

# Thinking モード — 複雑なタスク向けの深い構造化推論
python3 agent_skill.py chat --prompt "コーヒーブランドの VI 一式をデザインして" \
  --mode thinking --json --download

# プロジェクト管理
python3 agent_skill.py projects
python3 agent_skill.py project-add --project-id NEW_ID --name "ブランドキット"
python3 agent_skill.py project-switch --project-id NEW_ID
python3 agent_skill.py threads
```

## 🎯 モデル選択

Agent が使用するモデルを制御する 3 つの方法：

1. **プロンプトで言及**（最もシンプル）— `"kling で波の動画を生成して"`
2. **`--prefer-models`**（ソフトプリファレンス）— `'{"IMAGE":["generate_image_midjourney"]}'`
3. **`--include-tools`**（ハードコンストレイント）— `upscale_image`

利用可能なモデル：

| カテゴリ | Tool name | 表示名 | プレミアム |
|---|---|---|---|
| 画像 | `generate_image_gpt_image_2` | GPT Image 2 Auto |  |
| 画像 | `generate_image_gpt_image_2_low` | GPT Image 2 Low |  |
| 画像 | `generate_image_gpt_image_2_medium` | GPT Image 2 Medium |  |
| 画像 | `generate_image_gpt_image_2_high` | GPT Image 2 High |  |
| 画像 | `generate_image_nano_banana_pro` | Nano Banana Pro |  |
| 画像 | `generate_image_nano_banana_2` | Nano Banana 2 |  |
| 画像 | `generate_image_gpt_image_1_5` | GPT Image 1.5 |  |
| 画像 | `generate_image_seedream_v5` | Seedream 5.0 Lite |  |
| 画像 | `generate_image_flux_2_max` | Flux.2 Max |  |
| 画像 | `generate_image_flux_2_pro` | Flux.2 Pro |  |
| 画像 | `generate_image_seedream_v4_5` | Seedream 4.5 |  |
| 画像 | `generate_image_nano_banana` | Nano Banana |  |
| 画像 | `generate_image_seedream_v4` | Seedream 4 |  |
| 画像 | `generate_image_imagen_v4` | Gemini Imagen 4 |  |
| 画像 | `generate_image_midjourney` | Midjourney |  |
| 動画 | `generate_video_seedance_v2_0` | Seedance 2.0 | ⭐ |
| 動画 | `generate_video_seedance_v2_0_fast` | Seedance 2.0 Fast | ⭐ |
| 動画 | `generate_video_kling_v3` | Kling 3.0 | ⭐ |
| 動画 | `generate_video_kling_v3_omni` | Kling 3.0 Omni | ⭐ |
| 動画 | `generate_video_seedance_pro_v1_5` | Seedance 1.5 Pro |  |
| 動画 | `generate_video_kling_v2_6` | Kling 2.6 | ⭐ |
| 動画 | `generate_video_wan_v2_6` | Wan 2.6 |  |
| 動画 | `generate_video_sora_v2_pro` | Sora 2 Pro | ⭐ |
| 動画 | `generate_video_sora_v2` | Sora 2 | ⭐ |
| 動画 | `generate_video_veo3_1` | Veo 3.1 | ⭐ |
| 動画 | `generate_video_veo3_1_fast` | Veo 3.1 Fast | ⭐ |
| 動画 | `generate_video_kling_omni_v1` | Kling O1 | ⭐ |
| 動画 | `generate_video_hailuo_v2_3` | Hailuo 2.3 |  |
| 動画 | `generate_video_veo3` | Veo 3 | ⭐ |
| 動画 | `generate_video_vidu_q2` | Vidu Q2 |  |
| 3D | `generate_3d_tripo` | Tripo |  |

## 🧠 推論モード

`--mode` でリクエストごとの agent 推論方式を制御できます：

- **`fast`**（デフォルト） — 軽量なワンショット応答。高速・低コストで、単純な一発生成に適しています。
- **`thinking`** — 深い構造化推論で、先にプランニングしてから多段階の分析を行います。複雑なブランドシステムやマルチアセットのキャンペーンなど、熟慮を要するタスクに適しています。やや遅いですが品質が高い。

```bash
# 高速ワンショット（デフォルト）
python3 agent_skill.py chat --prompt "猫を描いて"

# 深い推論
python3 agent_skill.py chat --prompt "ブランドアイデンティティ一式をデザインして" --mode thinking
```

**モードは thread の初回メッセージ時に固定されます**。モードを切り替えるには新しい thread を開始してください（`--thread-id` を渡さない）。Lovart Web UI のモードトグルと同じ挙動です。

## ⚡ 生成モード

推論モードとは別で、これはアカウントレベルの永続的な課金設定です：

```bash
# 高速モード — クレジット消費、キューなし
python3 agent_skill.py set-mode --fast

# 無制限モード — 無料、キューあり
python3 agent_skill.py set-mode --unlimited

# 現在のモードを確認
python3 agent_skill.py query-mode
```

## 🚦 レート制限

API はエンドポイントの種類に応じて 2 段階のレート制限を適用します：

| 階層 | エンドポイント | 毎分 | 毎時 |
|------|---------------|------|------|
| **Chat**（書き込み系） | `/chat`、`/chat/confirm` | 60 | 600 |
| **Query**（読み取り系） | `/chat/status`、`/chat/result`、`/project/*`、`/mode/*` など | 300 | 3000 |

厳しい Chat 階層は生成タスクを保護します。Query 階層はゆるやかで、ステータス/結果のポーリングが生成の予算を消費しません。

上限を超えると `HTTP 429` と `Retry-After: 60` ヘッダーを返します。

これとは別に**生成の同時実行制限**があり、各 thread で一度に実行できる生成タスクは 1 つだけです。そのスレッドでタスク実行中に新しいリクエストを送ると `HTTP 409` で拒否されます。異なる thread 間では並行実行が可能です。

Skill はネットワークの一時的なエラーに対して自動リトライ（3 回バックオフ）しますが、レート制限や課金エラーは即座に返されます。

## 💾 ローカル状態

設定と会話履歴は `~/.lovart/state.json` に永続化されます：

```json
{
  "active_project": "abc123...",
  "projects": {
    "abc123...": {"name": "マイプロジェクト", "created_at": "..."}
  },
  "threads": [
    {"id": "xxx", "project_id": "abc123...", "topic": "サイバーパンク猫", "updated_at": "..."}
  ]
}
```

## 🤖 統合方法

### OpenClaw（推奨）

```bash
npx skills add lovartai/lovart-skill
```

本 skill は [OpenClaw](https://openclaw.com) のファーストクラス skill として設計されています。インストール後、AI Agent が自動検出して呼び出します。環境変数の設定以外、追加の設定は不要です。

### その他の AI アシスタント

Claude Code、Cursor など、Python スクリプトを実行可能なアシスタントにも対応しています。完全な統合仕様は `SKILL.md` を参照してください。

## 📁 プロジェクト構成

```
lovart-skill/
├── README.md
├── README_CN.md
├── README_TW.md
├── README_JA.md
└── skills/
    └── lovart-skill/
        ├── SKILL.md          # Skill 仕様ファイル (OpenClaw 規格)
        └── agent_skill.py    # Python クライアント (依存ゼロ)
```

## 🔒 セキュリティとプライバシー

- **ローカル状態ファイル**：skill は `~/.lovart/state.json` を読み書きしてアクティブプロジェクトと最近のスレッド ID を保存します。その他のファイルにはアクセスしません
- **外部通信**：Lovart API (`https://lgw.lovart.ai`) と Lovart CDN（生成物のダウンロード用）のみを呼び出します。第三者サービスは使用しません
- **API キー**：AK/SK は環境変数 (`LOVART_ACCESS_KEY` / `LOVART_SECRET_KEY`) から読み込まれ、リクエストごとに HMAC-SHA256 で署名されます。キーはディスクに保存されず、ログにも出力されません
- **TLS**：**SSL 証明書検証はデフォルトで有効**。TLS インターセプトを行う企業プロキシ/VPN 環境下でのみ `LOVART_INSECURE_SSL=1` で無効化できます
- **ソースコード**：`skills/lovart-skill/agent_skill.py` は約 900 行の純粋な Python 標準ライブラリコード。インストール前に一読することをお勧めします

## 🏗️ アーキテクチャ

```
ユーザー -> OpenClaw / Claude Code / その他 AI アシスタント
              -> agent_skill.py (本 skill)
                -> Lovart OpenAPI (AK/SK HMAC-SHA256 署名認証)
                  -> Lovart AI Agent (モデル選択、ワークフロー編成)
                    -> 生成された画像 / 動画 / 音声
```

## 🤝 コントリビュート

コントリビュート歓迎です！

- [Issue を作成](https://github.com/lovartai/lovart-skill/issues) してバグ報告や機能提案ができます
- [Pull Request を送信](https://github.com/lovartai/lovart-skill/pulls) して問題の修正や改善ができます


## 📄 ライセンス

[MIT](LICENSE)
