# Fallback-only fork

This fork of [fivetaku/insane-search](https://github.com/fivetaku/insane-search) keeps the engine as it is and changes only when it runs: insane-search steps in after a normal fetch has failed, never before.

## What differs from upstream

| Upstream | This fork |
|---|---|
| Depends on `gptaku-core`, which adds a SessionStart rule telling the agent to use gptaku skills before WebSearch, WebFetch and Bash, a router on every prompt, and a WebFetch fallback hook | No dependency. The plugin ships only the WebFetch fallback hook (`hooks/`), adapted from gptaku-core |
| The skill description says to use it before WebFetch or curl, for any URL | The description says to use it only after a normal fetch failed (blocked, rate-limited, timed out, or no usable content) |
| The skill's Step 0 runs `setup/setup.sh ask`: a one-time GitHub star prompt, and an update-check SessionStart hook written into `~/.claude/settings.json` | Step 0 is removed. `setup/` is kept unchanged so upstream merges stay clean, but nothing calls it |
| Installed from the `gptaku-plugins` marketplace | This repo is its own marketplace (`.claude-plugin/marketplace.json`) |

The fallback hook fires for WebFetch only. A subagent whose only tool is WebFetch cannot call skills, so it reports the failure back, and the main agent then picks the skill by its description.

Set `INSANE_SEARCH_FALLBACK=off` to silence the hook.

## Install

```
claude plugin marketplace add tot0rokr/insane-search
claude plugin install insane-search@insane-search-fork
```

## Sync with upstream

```
git fetch upstream
git merge upstream/main
```

Conflicts can only come from the files this fork changes: `.claude-plugin/plugin.json` (version, description, no `dependencies`), the frontmatter and the removed Step 0 of `skills/insane-search/SKILL.md`, and the fork-only files `.claude-plugin/marketplace.json`, `hooks/`, and this file. After a merge, bump the `-fallback.N` suffix in both `plugin.json` and `marketplace.json` so installed copies pick up the update.
