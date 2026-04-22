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
  <strong>English</strong> | <a href="README_CN.md">简体中文</a> | <a href="README_TW.md">繁體中文</a> | <a href="README_JA.md">日本語</a>
</p>
<br/>

> AI Agent Skills for [Lovart](https://lovart.ai) — generate images, videos, and audio from your AI coding assistant.

## ✨ What it does

This skill connects [OpenClaw](https://openclaw.com) (and other AI coding assistants) to Lovart's Agent OpenAPI, enabling:

- 🖼️ **Image generation** — posters, logos, illustrations, banners, mockups, etc.
- 🎬 **Video generation** — clips, animations, product videos
- 🎵 **Audio generation** — BGM, songs, sound effects
- ✂️ **Image/video editing** — upscale, reframe, style transfer
- 🧊 **3D generation** — 3D models from text or images
- 📁 **Project & thread management** — multi-project support with local state persistence

## 📦 Install

```bash
npx skills add lovartai/lovart-skill
```

Then set your environment variables:

```bash
export LOVART_ACCESS_KEY="ak_xxx"
export LOVART_SECRET_KEY="sk_xxx"
```

Get your AK/SK from the Lovart platform (Avatar menu -> AK/SK Management).

> 🎉 **That's it!** The skill files will be added to your project. Your AI Agent will auto-discover and invoke them — no manual script execution needed.

## 🚀 Quick start

```bash
# Generate an image
python3 agent_skill.py chat --prompt "a cyberpunk cat in neon city" --json --download

# Generate a video
python3 agent_skill.py chat --prompt "ocean waves crashing on rocks, cinematic" --json --download

# Generate BGM
python3 agent_skill.py chat --prompt "lofi hip-hop, chill, study vibes" --json --download
```

## 🛠️ Commands

### Generation

| Command | Description |
|---------|-------------|
| `chat` | Send prompt, wait for completion, return all results at once. Main command. |
| `watch` | Send prompt and stream artifacts as they complete (NDJSON, incremental delivery) |
| `send` | Send prompt without waiting (returns thread_id immediately) |
| `confirm` | Confirm a pending high-cost operation (e.g. video), then wait |
| `result` | Get results for a thread |
| `status` | Check thread status |

### Project management

| Command | Description |
|---------|-------------|
| `projects` | List all projects |
| `project-add` | Add and switch to a project |
| `project-switch` | Switch active project (supports prefix match) |
| `project-rename` | Rename a project |
| `project-remove` | Remove a project and its threads |
| `create-project` | Create a new empty project on the server |

### Configuration

| Command | Description |
|---------|-------------|
| `config` | View/update local settings (`~/.lovart/state.json`) |
| `threads` | List saved conversation threads |
| `set-mode` | Switch between fast (credits) / unlimited (queue) mode |
| `query-mode` | Check current generation mode |

### File operations

| Command | Description |
|---------|-------------|
| `upload` | Upload a local file to CDN (returns URL) |
| `upload-artifact` | Upload a URL artifact to a project |
| `download` | Download artifacts from URLs |

## 💡 Usage examples

```bash
# Use an existing project
python3 agent_skill.py chat --project-id PROJECT_ID --prompt "draw a cat" --json --download

# Continue a conversation (thread reuse preserves context)
python3 agent_skill.py chat --thread-id THREAD_ID --prompt "make it blue" --json --download

# Stream artifacts as they complete (NDJSON, for multi-image/video requests)
python3 agent_skill.py watch --prompt "generate 4 variations of a cyberpunk cat"

# Edit with reference image
python3 agent_skill.py upload --file photo.jpg
python3 agent_skill.py chat --prompt "change the style to watercolor" --attachments "CDN_URL" --json --download

# Prefer a specific model
python3 agent_skill.py chat --prompt "draw a cat" \
  --prefer-models '{"IMAGE":["generate_image_midjourney"]}' --json --download

# Force a specific tool (e.g. upscale instead of re-generate)
python3 agent_skill.py chat --prompt "upscale this image" \
  --include-tools upscale_image --attachments "IMAGE_URL" --json --download

# Thinking mode — deep structured reasoning for complex requests
python3 agent_skill.py chat --prompt "design a brand identity for a coffee startup" \
  --mode thinking --json --download

# Project management
python3 agent_skill.py projects
python3 agent_skill.py project-add --project-id NEW_ID --name "My Brand Kit"
python3 agent_skill.py project-switch --project-id NEW_ID
python3 agent_skill.py threads
```

## 🎯 Model selection

You can control which model the Agent uses in three ways:

1. **In the prompt** (simple) — `"generate ocean waves video using kling"`
2. **`--prefer-models`** (soft preference) — `'{"IMAGE":["generate_image_midjourney"]}'`
3. **`--include-tools`** (hard constraint) — `upscale_image`

Available models:

<!-- AUTOGEN:models:start -->

| Category | Tool name | Display name | Premium |
|---|---|---|---|
| IMAGE | `generate_image_flux_2_max` | Flux.2 Max |  |
| IMAGE | `generate_image_flux_2_pro` | Flux.2 Pro |  |
| IMAGE | `generate_image_gpt_image` | GPT Image |  |
| IMAGE | `generate_image_gpt_image_1_5` | GPT Image 1.5 |  |
| IMAGE | `generate_image_gpt_image_2` | GPT Image 2 Auto |  |
| IMAGE | `generate_image_gpt_image_2_high` | GPT Image 2 High |  |
| IMAGE | `generate_image_gpt_image_2_low` | GPT Image 2 Low |  |
| IMAGE | `generate_image_gpt_image_2_medium` | GPT Image 2 Medium |  |
| IMAGE | `generate_image_imagen_v4` | Gemini Imagen 4 |  |
| IMAGE | `generate_image_midjourney` | Midjourney |  |
| IMAGE | `generate_image_nano_banana` | Nano Banana |  |
| IMAGE | `generate_image_nano_banana_2` | Nano Banana 2 |  |
| IMAGE | `generate_image_nano_banana_pro` | Nano Banana Pro |  |
| IMAGE | `generate_image_seedream_v4` | Seedream 4 |  |
| IMAGE | `generate_image_seedream_v4_5` | Seedream 4.5 |  |
| IMAGE | `generate_image_seedream_v5` | Seedream 5.0 Lite |  |
| VIDEO | `gemini_veo2` | Gemini Veo 2 |  |
| VIDEO | `generate_video_hailuo_v02` | Hailuo-02 |  |
| VIDEO | `generate_video_hailuo_v2_3` | Hailuo 2.3 |  |
| VIDEO | `generate_video_kling_omni_v1` | Kling O1 | ⭐ Premium |
| VIDEO | `generate_video_kling_v2_5_turbo` | Kling 2.5 Turbo | ⭐ Premium |
| VIDEO | `generate_video_kling_v2_6` | Kling 2.6 | ⭐ Premium |
| VIDEO | `generate_video_kling_v3` | Kling 3.0 | ⭐ Premium |
| VIDEO | `generate_video_kling_v3_omni` | Kling 3.0 Omni | ⭐ Premium |
| VIDEO | `generate_video_ltx_v2` | LTXV 2.0 |  |
| VIDEO | `generate_video_seedance_pro_v1_5` | Seedance 1.5 Pro |  |
| VIDEO | `generate_video_seedance_v2_0` | Seedance 2.0 | ⭐ Premium |
| VIDEO | `generate_video_seedance_v2_0_fast` | Seedance 2.0 Fast | ⭐ Premium |
| VIDEO | `generate_video_sora_v2` | Sora 2 | ⭐ Premium |
| VIDEO | `generate_video_sora_v2_pro` | Sora 2 Pro | ⭐ Premium |
| VIDEO | `generate_video_veo3` | Veo 3 | ⭐ Premium |
| VIDEO | `generate_video_veo3_1` | Veo 3.1 | ⭐ Premium |
| VIDEO | `generate_video_veo3_1_fast` | Veo 3.1 Fast | ⭐ Premium |
| VIDEO | `generate_video_vidu_q2` | Vidu Q2 |  |
| VIDEO | `generate_video_wan_v2_5` | Wan 2.5 |  |
| VIDEO | `generate_video_wan_v2_6` | Wan 2.6 |  |
| VIDEO | `kling_1_6` | Kling 1.6 |  |
| VIDEO | `minimax_video_generator` | Hailuo-01 |  |
| VIDEO | `runway` | Runway Gen4 |  |
| 3D | `generate_3d_rodin` | Rodin |  |
| 3D | `generate_3d_tripo` | Tripo |  |

<!-- AUTOGEN:models:end -->

## 🧠 Reasoning modes

Control how the agent thinks per request via `--mode`:

- **`fast`** (default) — lightweight single-pass response. Faster, cheaper, suitable for simple one-shot generations.
- **`thinking`** — deep structured reasoning with planning and multi-step analysis. Use for complex brand systems, multi-asset campaigns, anything that benefits from deliberate planning. Slower but higher quality.

```bash
# Quick, single-shot (default)
python3 agent_skill.py chat --prompt "draw a cat"

# Deliberate, plan-first reasoning
python3 agent_skill.py chat --prompt "design a full brand identity" --mode thinking
```

**Mode is locked to the thread on its first message.** To switch modes, start a new thread (omit `--thread-id`). Mirrors the Lovart web UI toggle.

## ⚡ Billing modes

Separate from reasoning mode. This is a persistent account-level billing setting:

```bash
# Fast — costs credits, no queue
python3 agent_skill.py set-mode --fast

# Unlimited — free, may queue
python3 agent_skill.py set-mode --unlimited

# Check current
python3 agent_skill.py query-mode
```

## 🚦 Rate limits

The API enforces per-account request frequency limits, split into two tiers based on the endpoint you hit:

| Tier | Endpoints | Per minute | Per hour |
|------|-----------|-----------|---------|
| **Chat** (write) | `/chat`, `/chat/confirm` | 60 | 600 |
| **Query** (read) | `/chat/status`, `/chat/result`, `/project/*`, `/mode/*`, everything else | 300 | 3000 |

The stricter `Chat` tier protects generation. The `Query` tier is much looser so polling for status/results doesn't eat into your generation budget.

Exceeding a limit returns `HTTP 429` with `Retry-After: 60`.

This is separate from **generation concurrency** — each thread can only run one generation task at a time. If a task is already running in a thread, new requests to that thread are rejected with `HTTP 409` until it finishes. You can run tasks in different threads concurrently.

The skill auto-retries on transient network errors (3 attempts with backoff), but rate limit and billing errors are returned immediately.

## 💾 Local state

Settings and thread history are persisted at `~/.lovart/state.json`:

```json
{
  "active_project": "abc123...",
  "projects": {
    "abc123...": {"name": "My Project", "created_at": "..."}
  },
  "threads": [
    {"id": "xxx", "project_id": "abc123...", "topic": "cyberpunk cat", "updated_at": "..."}
  ]
}
```

## 🤖 Integration

### OpenClaw (recommended)

```bash
npx skills add lovartai/lovart-skill
```

This skill is designed as a first-class [OpenClaw](https://openclaw.com) skill. After installation, the AI Agent will auto-discover and invoke it — no extra configuration needed beyond setting the env vars.

### Other AI assistants

The skill also works with Claude Code, Cursor, and any assistant that can invoke Python scripts. See `SKILL.md` for the full integration contract.

## 📁 Project structure

```
lovart-skill/
├── README.md
├── README_CN.md
├── README_TW.md
├── README_JA.md
└── skills/
    └── lovart-skill/
        ├── SKILL.md          # Skill contract (OpenClaw spec)
        └── agent_skill.py    # Python client (zero dependencies)
```

## 🔒 Security & privacy

- **Local state file**: The skill reads/writes `~/.lovart/state.json` to persist your active project and recent thread IDs. No other files are accessed.
- **Outbound calls**: Only talks to the Lovart API (`https://lgw.lovart.ai`) and Lovart CDN (for downloading your own generated artifacts). No third-party services.
- **API keys**: AK/SK are read from env vars (`LOVART_ACCESS_KEY` / `LOVART_SECRET_KEY`) and signed with HMAC-SHA256 per request. Keys are never logged or persisted to disk.
- **TLS**: SSL certificate verification is **enabled by default**. Set `LOVART_INSECURE_SSL=1` to disable (only if you're behind a corporate proxy/VPN that intercepts TLS).
- **Source code**: `skills/lovart-skill/agent_skill.py` is ~900 lines of pure Python standard library — you're encouraged to read it before installing.

## 🏗️ Architecture

```
User -> OpenClaw / Claude Code / other AI assistant
          -> agent_skill.py (this skill)
            -> Lovart OpenAPI (AK/SK HMAC-SHA256 auth)
              -> Lovart AI Agent (model selection, orchestration)
                -> Generated images / videos / audio
```

## 🤝 Contributing

Contributions are welcome! Feel free to:

- [Open an issue](https://github.com/lovartai/lovart-skill/issues) to report bugs or suggest features
- [Submit a pull request](https://github.com/lovartai/lovart-skill/pulls) to fix issues or add improvements


## 📄 License

[MIT](LICENSE)
