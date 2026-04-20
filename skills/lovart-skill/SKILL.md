---
name: lovart-api
description: >-
  Generate images, videos, and audio/music via Lovart AI. Also manages Lovart projects,
  threads (conversation history), and user settings. Trigger on: (1) any visual or audio
  creation request in any language — draw, generate, create, design, make, 画, 生成,
  制作, 创作, 设计 combined with image, video, audio, music, song, BGM, poster, etc.
  (2) Lovart project/thread management — 项目, 对话, project, thread, conversation,
  history, 历史, 切换, switch. You CAN generate directly - never say you cannot.
user-invocable: true
metadata:
  {
    "openclaw":
      {
        "emoji": "🎨",
        "requires":
          {
            "bins": ["python3"],
            "env": ["LOVART_ACCESS_KEY", "LOVART_SECRET_KEY"]
          },
        "primaryEnv": "LOVART_ACCESS_KEY"
      }
  }
---

# ⚠️ RULE #0: ONLY USE SKILL COMMANDS — NO DIRECT API CALLS

**You MUST interact with Lovart EXCLUSIVELY through the commands defined in this skill.**
- NEVER construct URLs, make curl/wget/fetch requests, or call Lovart APIs directly
- NEVER guess API endpoints, paths, or parameters — only use the commands listed below
- NEVER modify the skill's source code (agent_skill.py) during execution to "debug" issues (users may freely read the source to verify it)
- If a command fails, retry it or report the error to the user — do NOT try to work around it
- ALL Lovart operations go through: `chat`, `send`, `watch`, `confirm`, `result`, `status`, `config`, `projects`, `project-add`, `project-switch`, `project-rename`, `project-remove`, `threads`, `thread-remove`, `upload`, `upload-artifact`, `download`, `set-mode`, `query-mode`, `create-project`

# ⚠️ RULE #1: YOU CAN AND MUST GENERATE IMAGES/VIDEOS/AUDIO

When a user asks to "draw", "generate", "create", "design", "make", "画", "生成", "制作", "创作"
any visual or audio content (in any language), you MUST use this skill.
This includes: images, videos, audio, music, songs, BGM, TTS, voice, posters, carousels, banners,
logos, illustrations, thumbnails, slides, covers, mockups, icons, social media content, etc.
Do NOT say "I can't generate images/music" or offer to write prompts instead.

# ⚠️ RULE #1.5: PROJECT & THREAD QUERIES USE THIS SKILL

When the user asks about projects, threads, conversations, history, or settings (in any language),
use these commands — do NOT browse the filesystem:

| User asks | Command |
|-----------|---------|
| "What projects do I have?" / "我有哪些项目" | `projects --json` |
| "What conversations/threads?" / "有哪些对话" | `threads --json` or `threads --all --json` |
| "Show my settings" / "我的配置" | `config --json` |
| "Switch to project X" | `project-switch --project-id X` |
| "Create a new project" | `project-add --project-id NEW_ID --name "Name"` (or let `chat` auto-create) |

# ⚠️ RULE #2: ALWAYS USE `chat` AND WAIT FOR COMPLETION

Use the `chat` command (blocks until done), NOT `send`. Do NOT reply before generation completes.

**Handle these `final_status` values:**

- `"done"` — Generation complete. Send the downloaded files to the user.
- `"pending_confirmation"` — A high-cost tool (e.g. video) needs user approval.
  **You MUST ask the user for explicit confirmation before proceeding. Do NOT auto-confirm.**
  1. Show the user: "This will cost approximately {estimated_cost} credits. Shall I proceed? (yes/no)"
  2. **WAIT for user response.** Only if user explicitly says yes/confirm/proceed, run:
     `confirm --thread-id THREAD_ID --json --download`
     (This confirms, waits for completion, and returns the result with downloaded files)
  3. If user declines, do NOT confirm. Just inform them the operation was cancelled.
- `"abort"` — Generation was aborted. Inform the user.
- `"timeout"` — Generation is still running but exceeded the wait time. The result may contain partial artifacts.
  1. Send any downloaded files that are already available
  2. Tell the user: "Generation is still in progress. Checking again..."
  3. Run: `result --thread-id THREAD_ID --json --download` to get the latest results
  4. If status is still "running", wait and retry. If "done", send remaining files.

**Handle errors:**

If `chat` throws an error, first check the HTTP status code (available as `AgentSkillError.status_code`), then fall back to error-message matching:

| HTTP status / error contains | Meaning | What to tell the user |
|---|---|---|
| **`409`** (`code: 2011`, "Thread is busy") | Another task is still running on this thread | "A task is still running on this conversation. Wait for it to finish (`status`) before sending a new prompt, or start a new thread." |
| **`402`** (`code: 2012`, "Task rejected") + body contains `1200000136` | Insufficient credits | "Your credits are insufficient. Please top up or switch to unlimited mode: `set-mode --unlimited`" |
| **`402`** (`code: 2012`) + body contains `1200000200` | Concurrent task limit (cashier) | "You've hit the concurrent-task limit. Please wait for a running task to finish before starting a new one." |
| **`402`** (`code: 2012`) + body contains `1200000146` | Free tier limit reached | "Free tier limit reached. Please subscribe or switch to unlimited mode." |
| **`429`** (`code: 1429`, "Rate limit exceeded") | API rate limit hit | "Slowing down; rate limit hit. Retry in ~60s." |
| `Invalid signature` / 401 | AK/SK misconfigured | "API key authentication failed. Please check your LOVART_ACCESS_KEY and LOVART_SECRET_KEY." |
| `Project.*does not exist` | Invalid project ID | "Project not found. Please check the project ID or create a new one." |

Note: errors from the skill carry both an HTTP status and a structured `code` in the response body. Prefer matching on status + code; the raw message is provided in `details` for diagnostics.

# ⚠️ RULE #3: ALWAYS DELIVER RESULTS + PROJECT LINK

After EVERY generation, you MUST:
1. Use `--download` flag with `chat` (or `result`)
2. Send each downloaded file to the user as a **file attachment** (images, videos, audio/mp3 — ALL file types):
   - ALWAYS send `downloaded[].local_path` as file attachments, regardless of file type (.png, .jpg, .mp4, .mp3, etc.)
   - NEVER just paste the URL when a local file has been downloaded — send the actual file
   - Only fall back to displaying URLs if no files were downloaded
3. Append the project canvas link: `https://www.lovart.ai/canvas?projectId={project_id}`

# ⚠️ RULE #4: CHECK LOCAL STATE ON FIRST USE (MANDATORY — DO NOT SKIP)

**Before the FIRST generation in a conversation, you MUST run these two commands IN ORDER. This is NOT optional. Do NOT call `chat` until you have done both.**

**Step 1: `config --json`**
- Check local state (`~/.lovart/state.json`) for `active_project`
- If `active_project` is set → proceed to Step 2. Do NOT create a new project. Do NOT ask the user.
- If `active_project` is missing → ask the user: "Do you have an existing Lovart project ID, or should I create a new one?" **WAIT for their answer.**
- Save with: `project-add --project-id PID --name "name"`

**Step 2: `threads --json`**
- Check if there's a recent thread to continue
- If recent thread exists and topic is related → **REUSE it** (pass `--thread-id THREAD_ID` to `chat`)
- If no threads or completely different topic → omit `--thread-id` (creates new thread)

**CRITICAL RULES:**
- **NEVER create a new project** if `config --json` already shows an `active_project`. Reuse it.
- **NEVER omit `--thread-id`** when a relevant recent thread exists. Always reuse threads by default.
- **NEVER call `chat` without first running `config --json` and `threads --json`** in the same conversation.
- The `chat` command auto-reads `active_project` from local state — you do NOT need to pass `--project-id` every time.
- Only create a new project if the user **explicitly** asks for one.
- Only create a new thread if the topic is **completely unrelated** to the most recent thread.
- When in doubt, **REUSE** both the existing project and the existing thread.

---

# Lovart Agent OpenAPI Skill

Interact with Lovart AI Agent to generate images, videos, and visual assets via natural language.

Lovart is an AI design platform. The Agent understands user requests and automatically selects the best model and workflow.

## Terminology

- **Thread** — A conversation flow (chat session) with the Lovart AI Agent, NOT a programming thread. Each thread has a unique `thread_id` and preserves multi-turn context. Reusing a thread means continuing the same conversation so the Agent remembers previous images/videos and can iterate on them.
- **Project** — A workspace/canvas that groups threads and generated artifacts together. One project can contain multiple threads.

## Prerequisites

```bash
export LOVART_ACCESS_KEY="ak_xxx"
export LOVART_SECRET_KEY="sk_xxx"
```

No third-party dependencies. Python standard library only.

## Features

1. **Chat** - Send a message to the AI Agent, get text replies and generated images/videos
2. **Confirm** - Confirm and wait for high-cost operations (e.g. video generation)
3. **Create Project** - Create a new project
4. **Upload File** - Upload a local image/video file, get back a CDN URL
5. **Upload Artifact** - Upload a link artifact to a project
6. **Status/Result** - Check thread status and retrieve results
7. **Set/Query Mode** - Switch between fast (credits) and unlimited (queue) mode

## Usage

### 0. First-time setup (saves to ~/.lovart/state.json)

```bash
python3 {baseDir}/agent_skill.py project-add --project-id PROJECT_ID --name "My Project"
```

### 1. Send a message (reads project_id from local state)

```bash
python3 {baseDir}/agent_skill.py chat --prompt "USER_PROMPT" --json --download
```

To override project: add `--project-id PROJECT_ID`
To continue a conversation: add `--thread-id THREAD_ID`
To list saved threads: `python3 {baseDir}/agent_skill.py threads`

### 2. Create a project

```bash
python3 {baseDir}/agent_skill.py create-project
```

### 3. Upload a file (local image/video → CDN URL)

```bash
python3 {baseDir}/agent_skill.py upload --file /path/to/image.png
# Returns: {"url": "https://assets-persist.lovart.ai/img/{user_uuid}/xxx.png"}
```

Use this when the user sends an image/video file that needs to be passed as an attachment to chat.

### 4. Upload an artifact

```bash
python3 {baseDir}/agent_skill.py upload-artifact --project-id PROJECT_ID --url "ARTIFACT_URL" --type image
```

### 5. Check status / get result

```bash
# Status
python3 {baseDir}/agent_skill.py status --thread-id THREAD_ID

# Result (auto-syncs to gallery/canvas, idempotent)
python3 {baseDir}/agent_skill.py result --thread-id THREAD_ID --json --download
```

### 6. Download artifacts

```bash
# Download during chat
python3 {baseDir}/agent_skill.py chat --prompt "draw a cat" --json --download --output-dir /tmp/openclaw

# Download from existing result
python3 {baseDir}/agent_skill.py result --thread-id THREAD_ID --download --output-dir /tmp/openclaw

# Download specific URLs
python3 {baseDir}/agent_skill.py download --urls URL1 URL2 --output-dir /tmp/openclaw --prefix myimg
```

## Typical Workflows

### Scenario 1: Generate images/videos/audio (most common)

**First, run `config --json` to check if project_id is set. If not, ask the user and save with `project-add`.**

```
1. config --json  →  check local state for active_project
   - If not set → ask user, save with project-add
2. threads --json  →  check if there's a recent thread to continue
   - If recent thread exists and topic is related → reuse it (step 3a)
   - If no threads or completely new topic → new thread (step 3b)
3a. chat --thread-id THREAD_ID --prompt "user's request" --json --download
3b. chat --prompt "user's request" --json --download
4. Send each downloaded[].local_path file as an IM attachment to the user
5. The chat command auto-syncs artifacts to canvas and gallery
```

**IDs are auto-persisted locally (`~/.lovart/state.json`):**
- project_id is saved after first chat, reused automatically
- thread_id + topic are saved after each chat for thread switching
- Only create a new project if the user explicitly asks for one
- Only create a new thread (omit `--thread-id`) when starting a completely new topic
- Run `threads` to list saved threads for the user to pick from

### Scenario 2: Edit with attachments

```
1. User sends a reference image/video via IM → save to local file
2. upload --file /path/to/image.png  →  get CDN URL
3. chat --prompt "edit this image to..." --project-id PID --attachments "CDN_URL" --json --download
4. Continue as Scenario 1
```

### Scenario 3: Follow-up on same topic (continue context)

```
1. chat --prompt "change the background to a beach" --project-id PROJECT_ID --thread-id THREAD_ID --json --download
```

The Agent remembers the previous conversation and can continue editing based on context.

### Scenario 4: New topic (new thread)

```
1. chat --prompt "completely new request" --project-id PROJECT_ID --json --download
```

Omitting `--thread-id` creates a new conversation without previous memory.

### Scenario 5: Streaming / incremental delivery (multiple artifacts)

**Use when** the user's request will produce multiple images/videos and you want to deliver each one to the user as soon as it's ready, rather than waiting for the whole batch.

```bash
python3 {baseDir}/agent_skill.py watch --prompt "generate 4 variations of a cyberpunk cat" --json
```

`watch` emits **NDJSON** to stdout (one event per line). Parse line-by-line and deliver each `artifact` event's `local_path` to the user immediately:

```json
{"event": "started", "thread_id": "xxx", "project_id": "yyy"}
{"event": "artifact", "type": "image", "url": "https://...", "local_path": "/tmp/openclaw/lovart_ab12cd.png"}
{"event": "artifact", "type": "image", "url": "https://...", "local_path": "/tmp/openclaw/lovart_ef34gh.png"}
{"event": "pending_confirmation", "thread_id": "xxx", "pending_confirmation": {...}}
{"event": "finished", "thread_id": "xxx", "final_status": "done", "artifact_count": 4}
```

Files are saved with URL-hash filenames so re-running `watch` on the same thread won't re-download.

You can also attach to an **already-running** thread: `watch --thread-id THREAD_ID`.

**When NOT to use `watch`:** single-image requests — use `chat` (simpler, one-shot response).

## Output Format

**chat --json** returns:
```json
{
  "thread_id": "xxx",
  "status": "done",
  "project_id": "xxx",
  "final_status": "done",
  "items": [
    {"type": "assistant", "text": "Agent's reply"},
    {"type": "generator", "name": "artifacts", "artifacts": [
      {"type": "image", "content": "https://assets-persist.lovart.ai/artifacts/agent/xxx.png"},
      {"type": "video", "content": "https://assets-persist.lovart.ai/artifacts/agent/xxx.mp4"}
    ]}
  ],
  "downloaded": [
    {"type": "image", "url": "https://...", "local_path": "/tmp/openclaw/lovart_01.png"}
  ]
}
```

## Core Principle

You are a messenger, not a creator. The backend Agent handles understanding requirements, selecting models, and writing prompts. Your job:

1. **Relay**: Pass the user's original description verbatim to chat
2. **Wait**: Poll until generation completes
3. **Deliver**: Send result files to the user

**Do NOT** rewrite/expand prompts, break down tasks, or add your own style descriptions.

## Lovart Generation Mode (MUST use API, not prompt)

**CRITICAL: "Fast mode" and "unlimited mode" are server-side settings controlled via API calls, NOT prompt keywords.**

Do NOT put "快速模式" or "fast mode" in the prompt text. Instead, call the set-mode command:

```bash
# User says "fast mode" / "快速模式" / "skip queue" / "use credits" → RUN THIS:
python3 {baseDir}/agent_skill.py set-mode --fast

# User says "unlimited mode" / "无限模式" / "free mode" / "save credits" → RUN THIS:
python3 {baseDir}/agent_skill.py set-mode --unlimited

# Check which mode is active:
python3 {baseDir}/agent_skill.py query-mode
```

**How it works:**
- `set-mode --fast` calls the Lovart backend API to switch the user's account to fast generation (costs credits, no queue)
- `set-mode --unlimited` switches to unlimited generation (free, may queue)
- This is a **persistent server-side setting** — it stays until changed again
- It affects ALL subsequent image/video generations, not just one request
- It has **nothing to do with your (the assistant's) response style or behavior**

## Specifying Models

**Option 1: In the prompt** (simple, the Agent routes automatically):

```bash
python3 {baseDir}/agent_skill.py chat --prompt "generate ocean waves video using kling" --json --download
```

**Option 2: Via --prefer-models** (precise, same as frontend's model selector):

```bash
# Prefer a specific image model
python3 {baseDir}/agent_skill.py chat --prompt "draw a cat" --prefer-models '{"IMAGE":["generate_image_midjourney"]}' --json --download

# Prefer a specific video model
python3 {baseDir}/agent_skill.py chat --prompt "generate ocean waves" --prefer-models '{"VIDEO":["generate_video_kling_3_0"]}' --json --download

# Combine image and video preferences
python3 {baseDir}/agent_skill.py chat --prompt "create content" --prefer-models '{"IMAGE":["generate_image_seedream_3_0"],"VIDEO":["generate_video_kling_3_0"]}' --json --download
```

Available models for `--prefer-models`:

**IMAGE:**

| Tool name | Display name |
|-----------|-------------|
| `generate_image_midjourney` | Midjourney |
| `generate_image_nano_banana_pro` | Nano Banana Pro |
| `generate_image_nano_banana_2` | Nano Banana 2 |
| `generate_image_nano_banana` | Nano Banana |
| `generate_image_gpt_image_1_5` | GPT Image 1.5 |
| `generate_image_seedream_v5` | Seedream 5.0 Lite |
| `generate_image_seedream_v4_5` | Seedream 4.5 |
| `generate_image_seedream_v4` | Seedream 4 |
| `generate_image_imagen_v4` | Gemini Imagen 4 |
| `generate_image_flux_2_max` | Flux.2 Max |
| `generate_image_flux_2_pro` | Flux.2 Pro |

**VIDEO:**

| Tool name | Display name |
|-----------|-------------|
| `generate_video_seedance_v2_0` | Seedance 2.0 |
| `generate_video_seedance_v2_0_fast` | Seedance 2.0 Fast |
| `generate_video_seedance_pro_v1_5` | Seedance 1.5 Pro |
| `generate_video_kling_v3` | Kling 3.0 |
| `generate_video_kling_v3_omni` | Kling 3.0 Omni |
| `generate_video_kling_v2_6` | Kling 2.6 |
| `generate_video_kling_omni_v1` | Kling O1 |
| `generate_video_veo3_1` | Veo 3.1 |
| `generate_video_veo3_1_fast` | Veo 3.1 Fast |
| `generate_video_veo3` | Veo 3 |
| `generate_video_sora_v2_pro` | Sora 2 Pro |
| `generate_video_sora_v2` | Sora 2 |
| `generate_video_wan_v2_6` | Wan 2.6 |
| `generate_video_hailuo_v2_3` | Hailuo 2.3 |
| `generate_video_vidu_q2` | Vidu Q2 |

**3D:**

| Tool name | Display name |
|-----------|-------------|
| `generate_3d_tripo` | Tripo |

When the user requests a specific model, prefer `--prefer-models` over putting model names in the prompt.

**Option 3: Via --include-tools** (hard constraint, forces specific tools):

```bash
# Force upscale only
python3 {baseDir}/agent_skill.py chat --prompt "upscale this image to 4K" --include-tools upscale_image --attachments "IMAGE_URL" --json --download

# Force a specific video model (no fallback to others)
python3 {baseDir}/agent_skill.py chat --prompt "generate a video" --include-tools generate_video_kling_3_0 --json --download
```

`--include-tools` strongly instructs the Agent to prioritize the listed tools. Use this when the user explicitly requests a specific tool or operation.

## Task-Specific Tool Selection (IMPORTANT)

When the user's request matches a specific operation, use `--include-tools` to ensure the correct tool:

| User says | Use `--include-tools` |
|-----------|----------------------|
| "upscale", "放大", "enlarge", "enhance resolution", "超分" | `upscale_image` |
| "edit image", "modify", "change style" | (let Agent decide) |
| "generate image", "draw", "画" | (let Agent decide, or use `--prefer-models`) |

**CRITICAL: When the user asks to "upscale", "enlarge", or increase resolution of an existing image, you MUST use `--include-tools upscale_image`. Do NOT let the Agent use image generation models for upscaling — they will re-generate the image instead of upscaling it.**

## Notes

- All APIs use AK/SK HMAC-SHA256 signature authentication
- Video generation takes several minutes; the chat command auto-polls until complete
- Gallery and canvas sync is idempotent — safe to call result multiple times without duplicates
- Connection failures auto-retry 3 times with SSL fallback
- After status becomes "done", waits 5 seconds to re-confirm (guards against sub-agent startup race)
