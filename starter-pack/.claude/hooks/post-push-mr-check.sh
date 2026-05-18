#!/usr/bin/env bash
# PostToolUse hook: after git push, check for unresolved MR/PR comments
# Supports both GitHub and GitLab
INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

# Only trigger on git push commands
if ! echo "$CMD" | grep -qE '^git push'; then
  exit 0
fi

# Find current branch
BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null)
if [ -z "$BRANCH" ] || [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
  exit 0
fi

# Detect VCS type and find open MR/PR
MR_NUMBER=""
MR_URL=""

if command -v glab &>/dev/null; then
  MR_JSON=$(glab mr list --source-branch="$BRANCH" --state=opened --json url,iid 2>/dev/null || true)
  MR_NUMBER=$(echo "$MR_JSON" | jq -r '.[0].iid // empty' 2>/dev/null)
  MR_URL=$(echo "$MR_JSON" | jq -r '.[0].url // empty' 2>/dev/null)
fi

if [ -z "$MR_NUMBER" ] && command -v gh &>/dev/null; then
  MR_JSON=$(gh pr list --head "$BRANCH" --state open --json number,url 2>/dev/null || true)
  MR_NUMBER=$(echo "$MR_JSON" | jq -r '.[0].number // empty' 2>/dev/null)
  MR_URL=$(echo "$MR_JSON" | jq -r '.[0].url // empty' 2>/dev/null)
fi

if [ -z "$MR_NUMBER" ]; then
  exit 0
fi

# Use fetch-mr-feedback.sh for structured analysis
HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
FEEDBACK_JSON=$("$HOOK_DIR/fetch-mr-feedback.sh" "$MR_NUMBER" 2>/dev/null || echo '{"summary":{"needs_fixes":false}}')

NEEDS_FIXES=$(echo "$FEEDBACK_JSON" | jq -r '.summary.needs_fixes')
CRITICAL_COUNT=$(echo "$FEEDBACK_JSON" | jq -r '.summary.critical // 0')
WARNING_COUNT=$(echo "$FEEDBACK_JSON" | jq -r '.summary.warning // 0')
HUMAN_COUNT=$(echo "$FEEDBACK_JSON" | jq -r '.summary.human // 0')

if [ "$NEEDS_FIXES" != "true" ]; then
  exit 0
fi

SUMMARY="Critical: ${CRITICAL_COUNT}, Warning: ${WARNING_COUNT}, Human comments: ${HUMAN_COUNT}"

jq -n --arg url "$MR_URL" --arg mr "$MR_NUMBER" --arg summary "$SUMMARY" '{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": ("You just pushed to a branch with an open MR/PR: " + $url + "\n\nFindings summary: " + $summary + "\n\n### Action rules:\n- **Critical findings** -> auto-fix, then re-invoke reviewer\n- **Warning findings** -> present to user for decision\n- **Human comments** -> present to user, FINAL AUTHORITY\n- **Suggestion** -> informational only\n\nRun `bash .claude/hooks/fetch-mr-feedback.sh " + $mr + "` for full structured findings.")
  }
}'
