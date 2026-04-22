"""
Lovart Agent OpenAPI Skill - Zero-dependency Python client.
All APIs use AK/SK HMAC-SHA256 authentication.
"""

import hashlib
import hmac
import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from typing import Optional

import os

# SSL context — verification ON by default. Opt-out via LOVART_INSECURE_SSL=1
# for users behind corporate proxies/VPNs that do TLS interception.
_ssl_ctx = ssl.create_default_context()
if os.environ.get("LOVART_INSECURE_SSL") == "1":
    _ssl_ctx.check_hostname = False
    _ssl_ctx.verify_mode = ssl.CERT_NONE


class AgentSkillError(Exception):
    def __init__(self, message: str, code: int = 0):
        self.message = message
        self.code = code
        super().__init__(message)


class AgentSkill:
    """Lovart Agent OpenAPI client."""

    def __init__(
        self,
        base_url: str,
        access_key: str,
        secret_key: str,
        timeout: int = 120,
        poll_interval: int = 3,
        path_prefix: str = "/v1/openapi",
    ):
        self.base_url = base_url.rstrip("/")
        self.access_key = access_key
        self.secret_key = secret_key
        self.timeout = timeout
        self.poll_interval = poll_interval
        self.prefix = path_prefix


    # ── HTTP ─────────────────────────────────────────────────────────

    def _sign(self, method: str, path: str) -> dict:
        ts = str(int(time.time()))
        sig = hmac.new(
            self.secret_key.encode(),
            f"{method}\n{path}\n{ts}".encode(),
            hashlib.sha256,
        ).hexdigest()
        return {
            "X-Access-Key": self.access_key,
            "X-Timestamp": ts,
            "X-Signature": sig,
            "X-Signed-Method": method,
            "X-Signed-Path": path,
        }

    def _request(self, method: str, path: str, body=None, params=None, retries: int = 3) -> dict:
        url = f"{self.base_url}{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params)

        data = json.dumps(body).encode() if body is not None else None
        last_err = None

        for attempt in range(retries):
            # Re-sign on each attempt (timestamp freshness)
            headers = self._sign(method, path)
            headers["Content-Type"] = "application/json"
            headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) LovartAgentSkill/1.0"
            req = urllib.request.Request(url, data=data, headers=headers, method=method)

            try:
                with urllib.request.urlopen(req, timeout=self.timeout, context=_ssl_ctx) as resp:
                    result = json.loads(resp.read().decode())
                    break
            except urllib.error.HTTPError as e:
                err = e.read().decode()
                # Retry on gateway errors (404 route mismatch, 502, 503, 429)
                if e.code in (404, 429, 502, 503) and attempt < retries - 1:
                    last_err = e
                    time.sleep(2 * (attempt + 1))
                    continue
                try:
                    d = json.loads(err)
                    msg = d.get("message", d.get("error", str(e)))
                    details = d.get("details", "")
                    if details:
                        msg = f"{msg}: {details}"
                    raise AgentSkillError(msg, e.code)
                except (json.JSONDecodeError, KeyError):
                    raise AgentSkillError(f"HTTP {e.code}: {err}", e.code)
            except (urllib.error.URLError, ssl.SSLError, ConnectionError, OSError) as e:
                last_err = e
                if attempt < retries - 1:
                    time.sleep(2 * (attempt + 1))
                    continue
                raise AgentSkillError(f"Connection failed after {retries} attempts: {e}")
        else:
            raise AgentSkillError(f"Connection failed: {last_err}")

        if isinstance(result, dict) and result.get("code", 0) != 0:
            raise AgentSkillError(result.get("message", "Unknown error"), result.get("code", -1))

        return result.get("data", result) if isinstance(result, dict) else result

    # ── Project ──────────────────────────────────────────────────────

    def save_project(self, project_id: str = "", canvas: str = "",
                     project_name: str = "", project_type: int = 3) -> dict:
        """Create (empty project_id) or update (with project_id) a project."""
        body = {
            "project_id": project_id,
            "canvas": canvas,
            "project_cover_list": [],
            "pic_count": 0,
            "project_type": project_type,
        }
        if project_name:
            body["project_name"] = project_name
        return self._request("POST", f"{self.prefix}/project/save", body=body)

    def rename_project(self, project_id: str, name: str) -> dict:
        """Rename an existing project (server-side)."""
        return self._request("POST", f"{self.prefix}/project/save", body={
            "action": "rename",
            "project_id": project_id,
            "project_name": name,
        })

    def create_project(self, project_type: int = 3) -> str:
        """Create a new project. Returns project_id."""
        result = self.save_project(project_type=project_type)
        return result.get("project_id", "")

    # ── Mode (unlimited/fast) ───────────────────────────────────────

    def set_mode(self, unlimited: bool) -> dict:
        """Set generation mode. unlimited=True (queue, no credits), unlimited=False (fast, costs credits)."""
        return self._request("POST", f"{self.prefix}/mode/set", body={"unlimited": unlimited})

    def query_mode(self) -> dict:
        """Query current mode and available models."""
        return self._request("POST", f"{self.prefix}/mode/query", body={})

    # ── Confirm (high-cost tool) ────────────────────────────────────

    def confirm(self, thread_id: str) -> dict:
        """Confirm a high-cost tool operation (e.g. video generation in fast mode)."""
        return self._request("POST", f"{self.prefix}/chat/confirm", body={"thread_id": thread_id})

    # ── File Upload ─────────────────────────────────────────────────

    def upload_file(self, local_path: str) -> str:
        """Upload a local file via openapi proxy. Returns the CDN URL.
        The server handles OSS credentials internally — no tokens exposed.
        """
        import os
        with open(local_path, "rb") as f:
            file_data = f.read()

        filename = os.path.basename(local_path)
        boundary = uuid.uuid4().hex

        # Build multipart body
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f"Content-Type: application/octet-stream\r\n\r\n"
        ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

        path = f"{self.prefix}/file/upload"
        headers = self._sign("POST", path)
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        headers["User-Agent"] = "LovartAgentSkill/1.0"

        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url, data=body, method="POST", headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=_ssl_ctx) as resp:
                result = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            err_body = e.read().decode()
            raise AgentSkillError(f"Upload failed ({e.code}): {err_body}")

        if result.get("code") != 0:
            raise AgentSkillError(f"Upload failed: {result.get('message', 'unknown error')}")

        return result["data"]["url"]

    # ── Artifact ─────────────────────────────────────────────────────

    def upload_artifact(self, project_id: str, artifact_url: str, artifact_type: str = "image") -> dict:
        """Upload a link artifact. Returns {"artifact_id", "artifact_content", ...}."""
        return self._request("POST", f"{self.prefix}/artifact/upload", body={
            "project_id": project_id,
            "artifact_type": artifact_type,
            "artifact_content": artifact_url,
        })

    # ── Download ─────────────────────────────────────────────────────

    @staticmethod
    def download_artifacts(result: dict, output_dir: str = "/tmp/openclaw", prefix: str = "lovart") -> list:
        """Download all artifacts from a result dict to local files.
        Idempotent: file names are derived from URL hash, and existing files are skipped.
        Returns list of {"type", "url", "local_path", "new": bool}."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        downloaded = []
        seen_urls = set()
        for item in result.get("items", []):
            for artifact in item.get("artifacts", []):
                url = artifact.get("content", "")
                atype = artifact.get("type", "unknown")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                ext = os.path.splitext(url.split("?")[0])[-1] or (
                    ".mp4" if atype == "video" else ".png"
                )
                url_hash = hashlib.sha1(url.encode()).hexdigest()[:12]
                local_path = os.path.join(output_dir, f"{prefix}_{url_hash}{ext}")
                if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                    downloaded.append({"type": atype, "url": url, "local_path": local_path, "new": False})
                    continue
                try:
                    req = urllib.request.Request(url, headers={
                        "User-Agent": "Mozilla/5.0",
                        "Referer": "https://www.lovart.ai/",
                    })
                    with urllib.request.urlopen(req, timeout=60, context=_ssl_ctx) as resp:
                        with open(local_path, "wb") as f:
                            f.write(resp.read())
                    downloaded.append({"type": atype, "url": url, "local_path": local_path, "new": True})
                except Exception:
                    downloaded.append({"type": atype, "url": url, "local_path": None, "error": "download failed", "new": False})
        return downloaded

    # ── Chat ─────────────────────────────────────────────────────────

    def send(self, prompt: str, project_id: str, attachments=None, thread_id=None,
             prefer_models=None, include_tools=None, exclude_tools=None,
             mode: Optional[str] = None) -> str:
        """Send a chat message. Returns thread_id.

        prefer_models: dict mapping category to list of tool names (soft preference)
        include_tools: list of tool names to force use (hard constraint)
        exclude_tools: list of tool names to exclude (hard constraint)
        mode: 'thinking' for deep structured reasoning, or 'fast' for
              lightweight single-pass. Default is 'fast' (matches the web
              UI). Mode is locked to the thread on the first message — to
              switch, start a new thread.
        """
        body = {"prompt": prompt, "project_id": project_id}
        if attachments:
            body["attachments"] = attachments
        if thread_id:
            body["thread_id"] = thread_id
        if mode:
            body["mode"] = mode
        tc = {}
        if prefer_models:
            tc["prefer_tool_categories"] = prefer_models
        if include_tools:
            tc["include_tools"] = include_tools
        if exclude_tools:
            tc["exclude_tools"] = exclude_tools
        if tc:
            body["tool_config"] = tc
        return self._request("POST", f"{self.prefix}/chat", body=body)["thread_id"]

    def get_status(self, thread_id: str) -> dict:
        return self._request("GET", f"{self.prefix}/chat/status", params={"thread_id": thread_id})

    def get_result(self, thread_id: str) -> dict:
        return self._request("GET", f"{self.prefix}/chat/result", params={"thread_id": thread_id})

    def poll(self, thread_id: str, timeout: Optional[int] = None, verbose: bool = False) -> str:
        """Poll until done/abort/pending_confirmation. Returns final status.

        When status first becomes "done", waits a few seconds and re-checks
        to guard against a race where sub-agents (e.g. video generation)
        haven't started yet and the thread briefly appears done.

        Returns "pending_confirmation" if a high-cost tool needs user approval.
        """
        import sys
        deadline = time.time() + (timeout or self.timeout)
        confirm_delay = 5  # seconds to wait before confirming "done"
        poll_count = 0
        self._pending_confirmation = None  # reset per-call
        while time.time() < deadline:
            s = self.get_status(thread_id)
            poll_count += 1
            if verbose:
                elapsed = int(time.time() + (timeout or self.timeout) - deadline)
                print(f"[{elapsed}s] status={s['status']}", file=sys.stderr)
            if s["status"] == "abort":
                return "abort"
            if s["status"] == "done":
                time.sleep(confirm_delay)
                s2 = self.get_status(thread_id)
                if s2["status"] in ("done", "abort"):
                    # Check if there's a pending confirmation hidden in the result
                    try:
                        result = self.get_result(thread_id)
                        pc = result.get("pending_confirmation")
                        if pc:
                            self._pending_confirmation = pc
                            return "pending_confirmation"
                    except Exception:
                        pass
                    return s2["status"]
                if verbose:
                    print("[poll] sub-agent still running, continuing...", file=sys.stderr)
            # After 20s of running, periodically check for pending_confirmation
            if poll_count >= 7 and s["status"] == "running" and poll_count % 3 == 0:
                try:
                    result = self.get_result(thread_id)
                    pc = result.get("pending_confirmation")
                    if pc:
                        self._pending_confirmation = pc
                        return "pending_confirmation"
                except Exception:
                    pass
            time.sleep(self.poll_interval)
        return "timeout"

    def validate_project(self, project_id: str) -> bool:
        """Check if a project ID exists (read-only)."""
        try:
            result = self._request("GET", f"{self.prefix}/project/validate",
                                   params={"project_id": project_id})
            return result.get("valid", False)
        except AgentSkillError:
            return False

    def get_project_name(self, project_id: str) -> str:
        """Get project name. Returns empty string if not found."""
        try:
            result = self._request("GET", f"{self.prefix}/project/validate",
                                   params={"project_id": project_id})
            return result.get("project_name", "")
        except AgentSkillError:
            return ""

    def chat(self, prompt: str, project_id: Optional[str] = None,
             attachments=None, thread_id=None,
             timeout=None, auto_create_project=True,
             prefer_models=None, include_tools=None, exclude_tools=None,
             mode: Optional[str] = None) -> dict:
        """Send → poll → get result. One-shot convenience method.

        mode: 'thinking' for deep reasoning, 'fast' for lightweight single-pass.
              Locked to the thread after the first message.
        """
        auto_created = False
        if not project_id:
            if auto_create_project:
                project_id = self.create_project()
                auto_created = True
            else:
                raise AgentSkillError("project_id is required")
        else:
            # Validate with retry — newly created projects may need a moment to sync
            if not self.validate_project(project_id):
                time.sleep(2)
                if not self.validate_project(project_id):
                    raise AgentSkillError(f"Project '{project_id}' does not exist")

        tid = self.send(prompt=prompt, project_id=project_id,
                        attachments=attachments, thread_id=thread_id,
                        prefer_models=prefer_models,
                        include_tools=include_tools, exclude_tools=exclude_tools,
                        mode=mode)
        status = self.poll(tid, timeout=timeout)

        if status == "pending_confirmation":
            pc = getattr(self, '_pending_confirmation', {})
            return {
                "thread_id": tid,
                "project_id": project_id,
                "final_status": "pending_confirmation",
                "pending_confirmation": pc,
                "items": [],
            }

        result = self.get_result(tid)
        result["final_status"] = status
        result["project_id"] = project_id

        # Detect "done but no artifact" — usually means the agent answered
        # with text (e.g. the upstream image model refused the prompt via
        # content moderation, timed out, or the LLM decided not to call any
        # tool). Surface the assistant text under a clear field so callers
        # don't silently mistake it for a successful generation.
        if status == "done":
            has_artifact = any(
                (it.get("artifacts") or [])
                for it in (result.get("items") or [])
            )
            if not has_artifact:
                assistant_texts = [
                    (it.get("text") or "").strip()
                    for it in (result.get("items") or [])
                    if it.get("text")
                ]
                result["generation_succeeded"] = False
                result["warning"] = (
                    "Thread ended without producing any artifact. The agent "
                    "responded with text only — the upstream model may have "
                    "refused the prompt (content moderation), timed out, or "
                    "the LLM chose not to call a generation tool."
                )
                if assistant_texts:
                    result["agent_message"] = "\n\n".join(assistant_texts)
            else:
                result["generation_succeeded"] = True

        # Auto-name project if it's still "Untitled", empty, or looks like a truncated ID
        if project_id:
            try:
                current_name = self.get_project_name(project_id)
                needs_rename = (
                    not current_name
                    or current_name.lower() in ("untitled", "")
                    or (len(current_name) <= 12 and project_id.startswith(current_name))
                )
                if needs_rename:
                    project_name = prompt[:30].strip()
                    self.rename_project(project_id, project_name)
                    result["project_name"] = project_name
            except Exception:
                pass

        return result


# ── Local State ─────────────────────────────────────────────────────

class LocalState:
    """Persistent local state with multi-project support.

    State structure:
    {
      "active_project": "project_id_1",
      "projects": {
        "project_id_1": {"name": "My Design", "created_at": "..."},
        "project_id_2": {"name": "Brand Kit", "created_at": "..."}
      },
      "threads": [
        {"id": "xxx", "project_id": "project_id_1", "topic": "...", "updated_at": "..."}
      ]
    }
    """

    def __init__(self, path: Optional[str] = None):
        import os
        self.path = path or os.path.expanduser("~/.lovart/state.json")

    def _ensure_dir(self):
        import os
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def load(self) -> dict:
        import os
        if not os.path.exists(self.path):
            return {}
        try:
            with open(self.path, "r") as f:
                data = json.load(f)
            # Migrate old format (flat project_id → multi-project)
            if "project_id" in data and "projects" not in data:
                old_pid = data.pop("project_id")
                data["active_project"] = old_pid
                data["projects"] = {old_pid: {"name": "default", "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime())}}
                self.save(data)
            return data
        except (json.JSONDecodeError, IOError):
            return {}

    def save(self, data: dict):
        self._ensure_dir()
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ── Project management ──

    def get_project_id(self) -> Optional[str]:
        return self.load().get("active_project")

    def get_projects(self) -> dict:
        return self.load().get("projects", {})

    def add_project(self, project_id: str, name: str = ""):
        data = self.load()
        projects = data.setdefault("projects", {})
        if project_id not in projects:
            projects[project_id] = {
                "name": name or project_id[:8],
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
            }
        elif name:
            projects[project_id]["name"] = name
        data["active_project"] = project_id
        self.save(data)

    def switch_project(self, project_id: str) -> bool:
        data = self.load()
        projects = data.get("projects", {})
        if project_id not in projects:
            # Allow switching to a new project by partial match
            matches = [pid for pid in projects if pid.startswith(project_id)]
            if len(matches) == 1:
                project_id = matches[0]
            else:
                return False
        data["active_project"] = project_id
        self.save(data)
        return True

    def rename_project(self, project_id: str, name: str):
        data = self.load()
        projects = data.get("projects", {})
        if project_id in projects:
            projects[project_id]["name"] = name
            self.save(data)

    def remove_project(self, project_id: str):
        data = self.load()
        projects = data.get("projects", {})
        projects.pop(project_id, None)
        if data.get("active_project") == project_id:
            data["active_project"] = next(iter(projects), None)
        # Remove associated threads
        data["threads"] = [t for t in data.get("threads", []) if t.get("project_id") != project_id]
        self.save(data)

    # ── Thread management ──

    def get_threads(self, project_id: Optional[str] = None) -> list:
        threads = self.load().get("threads", [])
        if project_id:
            threads = [t for t in threads if t.get("project_id") == project_id]
        return threads

    def remove_thread(self, thread_id: str):
        data = self.load()
        data["threads"] = [t for t in data.get("threads", []) if t["id"] != thread_id]
        self.save(data)

    def upsert_thread(self, thread_id: str, topic: str, project_id: Optional[str] = None):
        data = self.load()
        threads = data.get("threads", [])
        pid = project_id or data.get("active_project")
        found = False
        for t in threads:
            if t["id"] == thread_id:
                t["topic"] = topic
                t["project_id"] = pid
                t["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime())
                found = True
                break
        if not found:
            threads.insert(0, {
                "id": thread_id,
                "project_id": pid,
                "topic": topic,
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
            })
        data["threads"] = threads[:50]
        self.save(data)


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    import argparse
    import os
    import sys

    # Read from env vars, fall back to CLI args
    env_base_url = os.environ.get("LOVART_BASE_URL", "https://lgw.lovart.ai")
    env_ak = os.environ.get("LOVART_ACCESS_KEY", "")
    env_sk = os.environ.get("LOVART_SECRET_KEY", "")

    parser = argparse.ArgumentParser(description="Lovart Agent OpenAPI Skill")
    parser.add_argument("--base-url", default=env_base_url)
    parser.add_argument("--ak", default=env_ak)
    parser.add_argument("--sk", default=env_sk)
    parser.add_argument("--timeout", type=int, default=180)
    sub = parser.add_subparsers(dest="command")

    # chat
    p = sub.add_parser("chat")
    p.add_argument("--prompt", required=True)
    p.add_argument("--project-id", default=None)
    p.add_argument("--thread-id", default=None, help="Reuse thread for context continuity")
    p.add_argument("--attachments", nargs="*", default=None)
    p.add_argument("--json", action="store_true")
    p.add_argument("--download", action="store_true", help="Download artifacts to local files")
    p.add_argument("--output-dir", default="/tmp/openclaw", help="Download output directory")
    p.add_argument("--prefer-models", default=None,
                   help='JSON: model preferences by category, e.g. \'{"IMAGE":["generate_image_midjourney"]}\'')
    p.add_argument("--include-tools", nargs="*", default=None,
                   help="Force use only these tools, e.g. upscale_image")
    p.add_argument("--exclude-tools", nargs="*", default=None,
                   help="Exclude these tools")
    p.add_argument("--mode", choices=["thinking", "fast"], default=None,
                   help="Reasoning mode: 'thinking' for deep structured reasoning, 'fast' for lightweight single-pass. Locked per thread.")

    # send (non-blocking: just send, return thread_id immediately)
    p = sub.add_parser("send")
    p.add_argument("--prompt", required=True)
    p.add_argument("--project-id", default=None)
    p.add_argument("--thread-id", default=None, help="Reuse thread for context continuity")
    p.add_argument("--attachments", nargs="*", default=None)
    p.add_argument("--mode", choices=["thinking", "fast"], default=None,
                   help="Reasoning mode: 'thinking' or 'fast'. Locked per thread.")

    # watch (stream partial results: send + incremental polling, emits NDJSON per completed artifact)
    p = sub.add_parser("watch", help="Send a prompt (or attach to existing thread) and stream artifacts as they complete")
    p.add_argument("--prompt", default=None, help="Prompt to send. If omitted, must provide --thread-id")
    p.add_argument("--project-id", default=None)
    p.add_argument("--thread-id", default=None, help="Attach to an existing running thread")
    p.add_argument("--attachments", nargs="*", default=None)
    p.add_argument("--output-dir", default="/tmp/openclaw")
    p.add_argument("--interval", type=int, default=3, help="Poll interval in seconds")
    p.add_argument("--mode", choices=["thinking", "fast"], default=None,
                   help="Reasoning mode: 'thinking' or 'fast'. Locked per thread.")

    # create-project
    sub.add_parser("create-project")

    # upload-artifact
    p = sub.add_parser("upload-artifact")
    p.add_argument("--project-id", required=True)
    p.add_argument("--url", required=True)
    p.add_argument("--type", default="image", choices=["image", "video"])

    # upload (local file → server → OSS → returns CDN URL)
    p = sub.add_parser("upload")
    p.add_argument("--file", required=True, help="Local file path to upload")

    # confirm (confirms, polls until done, returns result)
    p = sub.add_parser("confirm")
    p.add_argument("--thread-id", required=True, help="Thread with pending high-cost operation")
    p.add_argument("--json", action="store_true")
    p.add_argument("--download", action="store_true", help="Download artifacts after completion")
    p.add_argument("--output-dir", default="/tmp/openclaw")

    # set-mode
    p = sub.add_parser("set-mode")
    p.add_argument("--unlimited", action="store_true", help="Enable unlimited mode (queue, no credits)")
    p.add_argument("--fast", action="store_true", help="Enable fast mode (costs credits)")

    # query-mode
    sub.add_parser("query-mode")

    # status
    p = sub.add_parser("status")
    p.add_argument("--thread-id", required=True)

    # result
    p = sub.add_parser("result")
    p.add_argument("--thread-id", required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--download", action="store_true", help="Download artifacts to local files")
    p.add_argument("--output-dir", default="/tmp/openclaw")

    # download (standalone: download from URLs)
    p = sub.add_parser("download")
    p.add_argument("--urls", nargs="+", required=True, help="Artifact URLs to download")
    p.add_argument("--output-dir", default="/tmp/openclaw")
    p.add_argument("--prefix", default="lovart")

    # config (local state management)
    p = sub.add_parser("config", help="View or update local state (~/.lovart/state.json)")
    p.add_argument("--json", action="store_true")

    # project management
    p = sub.add_parser("projects", help="List all projects")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("project-add", help="Add and activate a project")
    p.add_argument("--project-id", required=True)
    p.add_argument("--name", default="", help="Friendly name for the project")

    p = sub.add_parser("project-switch", help="Switch active project")
    p.add_argument("--project-id", required=True, help="Full or prefix of project_id")

    p = sub.add_parser("project-rename", help="Rename a project")
    p.add_argument("--project-id", required=True)
    p.add_argument("--name", required=True)

    p = sub.add_parser("project-remove", help="Remove a project and its threads")
    p.add_argument("--project-id", required=True)

    # threads (list saved threads)
    p = sub.add_parser("threads", help="List saved thread history")
    p.add_argument("--project-id", default=None, help="Filter by project")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("thread-remove", help="Remove a thread from local history")
    p.add_argument("--thread-id", required=True)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    state = LocalState()

    # Handle local-only commands (no AK/SK needed)
    if args.command == "config":
        data = state.load()
        if args.json:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            active = data.get("active_project", "(not set)")
            projects = data.get("projects", {})
            name = projects.get(active, {}).get("name", "") if active != "(not set)" else ""
            print(f"active project: {active}" + (f" ({name})" if name else ""))
            print(f"projects: {len(projects)}")
            print(f"threads: {len(data.get('threads', []))}")
            print(f"state file: {state.path}")
        sys.exit(0)

    if args.command == "projects":
        projects = state.get_projects()
        active = state.get_project_id()
        if args.json:
            print(json.dumps({"active": active, "projects": projects}, indent=2, ensure_ascii=False))
        else:
            if not projects:
                print("No projects. Use: project-add --project-id PID --name NAME")
            else:
                for pid, info in projects.items():
                    marker = " *" if pid == active else "  "
                    name = info.get("name", "")
                    threads = len(state.get_threads(pid))
                    print(f"{marker} {pid[:12]}... {name:20s} ({threads} threads)")
        sys.exit(0)

    if args.command == "project-add":
        state.add_project(args.project_id, args.name)
        # Sync name to server if AK/SK available and name provided
        if args.name and args.ak and args.sk:
            try:
                s = AgentSkill(base_url=args.base_url, access_key=args.ak, secret_key=args.sk)
                s.rename_project(args.project_id, args.name)
            except Exception:
                pass
        print(f"Added and switched to project: {args.project_id}" + (f" ({args.name})" if args.name else ""))
        sys.exit(0)

    if args.command == "project-switch":
        if state.switch_project(args.project_id):
            full_id = state.get_project_id()
            name = state.get_projects().get(full_id, {}).get("name", "")
            print(f"Switched to: {full_id}" + (f" ({name})" if name else ""))
        else:
            print(f"Error: project '{args.project_id}' not found", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    if args.command == "project-rename":
        state.rename_project(args.project_id, args.name)
        if args.ak and args.sk:
            try:
                s = AgentSkill(base_url=args.base_url, access_key=args.ak, secret_key=args.sk)
                s.rename_project(args.project_id, args.name)
            except Exception:
                pass
        print(f"Renamed: {args.project_id} → {args.name}")
        sys.exit(0)

    if args.command == "project-remove":
        state.remove_project(args.project_id)
        print(f"Removed project: {args.project_id}")
        sys.exit(0)

    if args.command == "threads":
        pid = getattr(args, "project_id", None)
        if getattr(args, "all", False):
            threads = state.get_threads()
        else:
            threads = state.get_threads(pid or state.get_project_id())
        if args.json:
            print(json.dumps(threads, indent=2, ensure_ascii=False))
        else:
            if not threads:
                print("No saved threads.")
            else:
                for i, t in enumerate(threads):
                    pid_short = t.get("project_id", "")[:8]
                    print(f"  {i+1}. [{t['id'][:8]}...] [{pid_short}] {t.get('topic', '(no topic)')}  ({t.get('updated_at', '')})")
        sys.exit(0)

    if args.command == "thread-remove":
        state.remove_thread(args.thread_id)
        print(f"Removed thread: {args.thread_id}")
        sys.exit(0)

    if not args.ak or not args.sk:
        print("Error: LOVART_ACCESS_KEY and LOVART_SECRET_KEY must be set "
              "(via env vars or --ak/--sk)", file=sys.stderr)
        sys.exit(1)

    skill = AgentSkill(base_url=args.base_url, access_key=args.ak,
                       secret_key=args.sk, timeout=args.timeout)

    try:
        if args.command == "chat":
            # Auto-fill project_id from local state if not provided
            project_id = args.project_id or state.get_project_id()

            prefer_models = json.loads(args.prefer_models) if args.prefer_models else None
            result = skill.chat(prompt=args.prompt, project_id=project_id,
                                attachments=args.attachments, thread_id=args.thread_id,
                                prefer_models=prefer_models,
                                include_tools=args.include_tools,
                                exclude_tools=args.exclude_tools,
                                mode=args.mode)

            # Auto-save state
            if result.get("project_id"):
                name = result.get("project_name", args.prompt[:30].strip())
                state.add_project(result["project_id"], name)
            if result.get("thread_id"):
                topic = args.prompt[:50].strip()
                state.upsert_thread(result["thread_id"], topic)
            # Auto-download if requested
            if args.download:
                dl = skill.download_artifacts(result, output_dir=args.output_dir)
                result["downloaded"] = dl

            if args.json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"Status: {result['final_status']}")
                print(f"Thread: {result['thread_id']}")
                print(f"Project: {result.get('project_id', 'N/A')}")
                for item in result.get("items", []):
                    if item.get("text"):
                        print(f"\n[{item['type']}] {item['text']}")
                    for a in item.get("artifacts", []):
                        print(f"  [{a['type']}] {a['content']}")
                for dl in result.get("downloaded", []):
                    if dl.get("local_path"):
                        print(f"  -> {dl['local_path']}")

        elif args.command == "send":
            project_id = args.project_id or state.get_project_id()
            if not project_id:
                project_id = skill.create_project()
            tid = skill.send(prompt=args.prompt, project_id=project_id,
                             attachments=args.attachments, thread_id=args.thread_id,
                             mode=args.mode)
            state.add_project(project_id, args.prompt[:30].strip())
            state.upsert_thread(tid, args.prompt[:50].strip())
            print(json.dumps({"thread_id": tid, "project_id": project_id}))

        elif args.command == "watch":
            if not args.thread_id and not args.prompt:
                print("Error: watch requires either --thread-id or --prompt", file=sys.stderr)
                sys.exit(1)

            # Either send a new prompt or attach to an existing thread
            if args.thread_id:
                tid = args.thread_id
                project_id = args.project_id or state.get_project_id()
            else:
                project_id = args.project_id or state.get_project_id()
                if not project_id:
                    project_id = skill.create_project()
                tid = skill.send(prompt=args.prompt, project_id=project_id,
                                 attachments=args.attachments, mode=args.mode)
                state.add_project(project_id, args.prompt[:30].strip())
                state.upsert_thread(tid, args.prompt[:50].strip())

            # Emit initial event
            print(json.dumps({"event": "started", "thread_id": tid, "project_id": project_id}, ensure_ascii=False), flush=True)

            # Stream: poll status + result, download new artifacts each round, emit NDJSON
            seen_urls = set()
            deadline = time.time() + skill.timeout
            final_status = "timeout"
            while time.time() < deadline:
                try:
                    status_info = skill.get_status(tid)
                    status = status_info.get("status", "running")
                    result = skill.get_result(tid)
                    dl = skill.download_artifacts(result, output_dir=args.output_dir)
                    for d in dl:
                        if d.get("url") in seen_urls or not d.get("new"):
                            if d.get("url") not in seen_urls and d.get("local_path"):
                                # Already on disk from previous run — still emit once
                                seen_urls.add(d["url"])
                                print(json.dumps({"event": "artifact", "type": d["type"], "url": d["url"], "local_path": d.get("local_path")}, ensure_ascii=False), flush=True)
                            continue
                        seen_urls.add(d["url"])
                        print(json.dumps({"event": "artifact", "type": d["type"], "url": d["url"], "local_path": d.get("local_path")}, ensure_ascii=False), flush=True)
                    pc = result.get("pending_confirmation")
                    if pc:
                        final_status = "pending_confirmation"
                        print(json.dumps({"event": "pending_confirmation", "thread_id": tid, "pending_confirmation": pc}, ensure_ascii=False), flush=True)
                        break
                    if status == "abort":
                        final_status = "abort"
                        break
                    if status == "done":
                        final_status = "done"
                        break
                except AgentSkillError as e:
                    print(json.dumps({"event": "error", "message": e.message}, ensure_ascii=False), flush=True)
                time.sleep(args.interval)

            print(json.dumps({"event": "finished", "thread_id": tid, "final_status": final_status, "artifact_count": len(seen_urls)}, ensure_ascii=False), flush=True)

        elif args.command == "confirm":
            skill.confirm(args.thread_id)
            # Poll until done after confirmation
            status = skill.poll(args.thread_id)
            result = skill.get_result(args.thread_id)
            result["final_status"] = status
            if args.download:
                dl = skill.download_artifacts(result, output_dir=args.output_dir)
                result["downloaded"] = dl
            if args.json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"Status: {status}")
                print(f"Thread: {args.thread_id}")
                for item in result.get("items", []):
                    if item.get("text"):
                        print(f"\n[{item['type']}] {item['text']}")
                    for a in item.get("artifacts", []):
                        print(f"  [{a['type']}] {a['content']}")
                for dl in result.get("downloaded", []):
                    if dl.get("local_path"):
                        print(f"  -> {dl['local_path']}")

        elif args.command == "set-mode":
            if args.fast:
                r = skill.set_mode(unlimited=False)
                print(json.dumps({"mode": "fast", "detail": r}, ensure_ascii=False))
            elif args.unlimited:
                r = skill.set_mode(unlimited=True)
                print(json.dumps({"mode": "unlimited", "detail": r}, ensure_ascii=False))
            else:
                print("Error: specify --fast or --unlimited", file=sys.stderr)
                sys.exit(1)

        elif args.command == "query-mode":
            r = skill.query_mode()
            mode = "unlimited" if r.get("unlimited") else "fast"
            print(json.dumps({"mode": mode, "detail": r}, indent=2, ensure_ascii=False))

        elif args.command == "create-project":
            pid = skill.create_project()
            state.add_project(pid)
            print(json.dumps({"project_id": pid}))

        elif args.command == "upload":
            url = skill.upload_file(args.file)
            print(json.dumps({"url": url}))

        elif args.command == "upload-artifact":
            r = skill.upload_artifact(args.project_id, args.url, args.type)
            print(json.dumps(r, indent=2, ensure_ascii=False))

        elif args.command == "status":
            print(json.dumps(skill.get_status(args.thread_id), indent=2))

        elif args.command == "result":
            r = skill.get_result(args.thread_id)
            if args.download:
                dl = skill.download_artifacts(r, output_dir=args.output_dir)
                r["downloaded"] = dl
            print(json.dumps(r, indent=2, ensure_ascii=False))

        elif args.command == "download":
            # Download from explicit URLs
            fake_result = {"items": [{"artifacts": [{"type": "image", "content": u} for u in args.urls]}]}
            dl = skill.download_artifacts(fake_result, output_dir=args.output_dir, prefix=args.prefix)
            print(json.dumps({"downloaded": dl, "output_dir": args.output_dir}, indent=2, ensure_ascii=False))

    except AgentSkillError as e:
        print(f"Error: {e.message}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
