#!/usr/bin/env python3
"""PostToolUse / PostToolUseFailure (WebFetch): if the page was blocked, point the agent at insane-search.

Adapted from gptaku-core's hooks/fetch_fallback.py (https://github.com/fivetaku/gptaku_plugins,
MIT). Unlike gptaku-core, this fork installs no SessionStart rule and no per-prompt router: this
hook is the only automatic trigger, and it fires only when a fetch actually failed.

A missing host (ENOTFOUND) or a refused connection is not passed on: insane-search cannot open
those either. Set INSANE_SEARCH_FALLBACK=off to silence the hook.
"""
import json
import os
import re
import sys

SKILL = "insane-search:insane-search"
BLOCKED = re.compile(r"(unable to fetch|safety check for domain|unable to verify if domain|certificate|"
                     r"\b(403|429|451|503)\b|forbidden|access denied|too many requests|just a moment|"
                     r"enable javascript|captcha|cloudflare|blocked|timed? ?out|timeout)", re.I)
UNREACHABLE = re.compile(r"(enotfound|econnrefused|doesn't want to proceed|rejected)", re.I)
# A successful response counts as blocked only when its body is a challenge page; plain words such
# as "blocked" inside normal content must not trigger the fallback.
CHALLENGE = re.compile(r"(just a moment|enable javascript|captcha|access denied)", re.I)

if os.environ.get("INSANE_SEARCH_FALLBACK") == "off":
    sys.exit(0)
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if data.get("tool_name") != "WebFetch":
    sys.exit(0)

event = data.get("hook_event_name", "PostToolUse")
url = (data.get("tool_input") or {}).get("url", "")
if event == "PostToolUseFailure":
    text = str(data.get("error", ""))
else:
    resp = data.get("tool_response")
    code = resp.get("code") if isinstance(resp, dict) else None
    body = (resp.get("result", "") if isinstance(resp, dict) else str(resp or ""))[:800]
    if isinstance(code, int) and code >= 400:
        text = f"{code} {body}"
    elif CHALLENGE.search(body):
        text = body
    else:
        sys.exit(0)
if UNREACHABLE.search(text) or not BLOCKED.search(text):
    sys.exit(0)

msg = (f"[insane-search] WebFetch could not open {url or 'this page'} (blocked or rate-limited). "
       f"Do not give up or guess: call the Skill tool with `{SKILL}` to open the same URL through public routes.")
print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": msg}}, ensure_ascii=False))
