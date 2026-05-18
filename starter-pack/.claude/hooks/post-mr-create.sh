#!/usr/bin/env bash
# PostToolUse hook: detect MR/PR creation and kick off Ralph Wiggum Loop
# Supports both GitHub (gh pr create) and GitLab (glab mr create)
INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // ""')
RESPONSE=$(echo "$INPUT" | jq -r '.tool_response // ""')

# Only trigger on MR/PR creation commands
if ! echo "$CMD" | grep -qE 'glab mr create|gh pr create'; then
  exit 0
fi

# Extract MR/PR URL from response
MR_URL=$(echo "$RESPONSE" | grep -oE 'https://[^ ]+(merge_requests|pull)/[0-9]+' | head -1)

if [ -z "$MR_URL" ]; then
  exit 0
fi

# Extract MR/PR number from URL
MR_NUMBER=$(echo "$MR_URL" | grep -oE '[0-9]+$')

# Detect VCS type
if echo "$CMD" | grep -q 'glab'; then
  VCS="gitlab"
  DIFF_CMD="glab mr diff $MR_NUMBER"
  COMMENT_CMD="glab mr note $MR_NUMBER --message"
  APPROVE_CMD="glab mr approve $MR_NUMBER"
else
  VCS="github"
  DIFF_CMD="gh pr diff $MR_NUMBER"
  COMMENT_CMD="gh pr comment $MR_NUMBER --body"
  APPROVE_CMD="gh pr review $MR_NUMBER --approve --body \"All checks pass.\""
fi

# Output JSON with Ralph Wiggum Loop instructions
jq -n --arg url "$MR_URL" --arg mr "$MR_NUMBER" --arg vcs "$VCS" \
      --arg diff_cmd "$DIFF_CMD" --arg comment_cmd "$COMMENT_CMD" \
      --arg approve_cmd "$APPROVE_CMD" '{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": ("A merge/pull request was just created: " + $url + "\n\n## RALPH WIGGUM LOOP — Automated Review Cycle\n\n### Step 1: Invoke Reviewer\nUse the Agent tool with subagent_type=reviewer. Tell the reviewer:\n- The MR/PR URL: " + $url + "\n- Fetch the diff via `" + $diff_cmd + "`\n- Apply the review checklist from .claude/agents/reviewer.md\n- Post each finding as a comment via `" + $comment_cmd + " \"...\"`\n- IMPORTANT: Prefix every comment with `**[Agent Review]** `\n- Classify findings as Critical, Warning, or Suggestion\n- If zero Critical findings, approve via `" + $approve_cmd + "`\n\n### Step 2: After Reviewer Returns\n- If APPROVED (zero Critical) → Tell the user the MR/PR is ready for human approval. Present any Warning findings for user decision.\n- If Critical findings → Continue to Step 3.\n\n### Step 3: Address Critical Findings ONLY\n- Invoke the implementer agent ONLY for Critical findings\n- Do NOT auto-fix Warnings — present them to the user\n\n### Step 4: Re-invoke Reviewer\nAfter implementer pushes fixes, ALWAYS re-invoke the reviewer.\nRepeat Steps 2-4 until zero Critical findings.\n\nIMPORTANT: Only Critical findings block approval. Warnings are presented to the user. Human comments have FINAL AUTHORITY. ALWAYS re-invoke reviewer after ANY fixes.")
  }
}'
