#!/usr/bin/env bash
# Fetch structured MR/PR feedback for implementer consumption.
# Usage: fetch-mr-feedback.sh <MR_NUMBER>
#
# Parses MR/PR comments and extracts reviewer findings classified by severity.
# Outputs JSON that the orchestrator can pass directly to the implementer agent.
# Supports both GitHub (gh) and GitLab (glab).

set -euo pipefail

MR_NUMBER="${1:?Usage: fetch-mr-feedback.sh <MR_NUMBER>}"

# Detect VCS type
VCS=""
NOTES_JSON="[]"

if command -v glab &>/dev/null; then
  # Try GitLab first
  MR_JSON=$(glab api "projects/:id/merge_requests/${MR_NUMBER}" 2>/dev/null || echo '{}')
  MR_BRANCH=$(echo "$MR_JSON" | jq -r '.source_branch // ""')
  MR_URL=$(echo "$MR_JSON" | jq -r '.web_url // ""')
  if [ -n "$MR_URL" ] && [ "$MR_URL" != "" ]; then
    VCS="gitlab"
    NOTES_JSON=$(glab api "projects/:id/merge_requests/${MR_NUMBER}/notes?per_page=100&sort=asc" 2>/dev/null || echo '[]')
  fi
fi

if [ -z "$VCS" ] && command -v gh &>/dev/null; then
  # Fall back to GitHub
  VCS="github"
  MR_JSON=$(gh pr view "$MR_NUMBER" --json headRefName,url 2>/dev/null || echo '{}')
  MR_BRANCH=$(echo "$MR_JSON" | jq -r '.headRefName // ""')
  MR_URL=$(echo "$MR_JSON" | jq -r '.url // ""')
  # GitHub comments via API
  REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner' 2>/dev/null || echo '')
  if [ -n "$REPO" ]; then
    NOTES_JSON=$(gh api "repos/${REPO}/issues/${MR_NUMBER}/comments" --paginate 2>/dev/null || echo '[]')
    # Normalize GitHub format to match GitLab structure
    NOTES_JSON=$(echo "$NOTES_JSON" | jq '[.[] | {author: {username: .user.login}, body: .body, created_at: .created_at, id: .id, system: false}]')
  fi
fi

if [ -z "$VCS" ]; then
  echo '{"error": "Neither gh nor glab CLI found"}' >&2
  exit 1
fi

# Extract findings by severity
CRITICAL=$(echo "$NOTES_JSON" | jq '[.[] | select(.system == false or .system == null) |
   select(.body | test("\\*\\*Critical\\*\\*|\\[Critical\\]|Severity:.*Critical"; "i")) |
   {author: .author.username, body: .body, created_at: .created_at, id: .id}]')

WARNING=$(echo "$NOTES_JSON" | jq '[.[] | select(.system == false or .system == null) |
   select(.body | test("\\*\\*Warning\\*\\*|\\[Warning\\]|Severity:.*Warning"; "i")) |
   {author: .author.username, body: .body, created_at: .created_at, id: .id}]')

INFO=$(echo "$NOTES_JSON" | jq '[.[] | select(.system == false or .system == null) |
   select(.body | test("\\*\\*Info\\*\\*|\\[Info\\]|Severity:.*Info|\\*\\*Suggestion\\*\\*|\\[Suggestion\\]"; "i")) |
   {author: .author.username, body: .body, created_at: .created_at, id: .id}]')

# Human comments: not system, not agent-generated, not severity-classified
HUMAN=$(echo "$NOTES_JSON" | jq '[.[] | select(.system == false or .system == null) |
   select(.body | test("^\\*\\*\\[Agent Review\\]\\*\\*|^\\[Agent Review\\]|^\\*\\*\\[Agent "; "m") | not) |
   select(.body | test("\\*\\*Critical\\*\\*|\\*\\*Warning\\*\\*|\\*\\*Info\\*\\*|\\*\\*Suggestion\\*\\*|\\[Critical\\]|\\[Warning\\]|\\[Info\\]|\\[Suggestion\\]"; "i") | not) |
   select(.body | length > 5) |
   {author: .author.username, body: .body, created_at: .created_at, id: .id}]')

CRITICAL_COUNT=$(echo "$CRITICAL" | jq 'length')
WARNING_COUNT=$(echo "$WARNING" | jq 'length')
INFO_COUNT=$(echo "$INFO" | jq 'length')
HUMAN_COUNT=$(echo "$HUMAN" | jq 'length')

jq -n \
  --arg mr "$MR_NUMBER" \
  --arg branch "$MR_BRANCH" \
  --arg url "$MR_URL" \
  --arg vcs "$VCS" \
  --argjson critical "$CRITICAL" \
  --argjson warning "$WARNING" \
  --argjson info "$INFO" \
  --argjson human "$HUMAN" \
  --argjson critical_count "$CRITICAL_COUNT" \
  --argjson warning_count "$WARNING_COUNT" \
  --argjson info_count "$INFO_COUNT" \
  --argjson human_count "$HUMAN_COUNT" \
  '{
    mr_number: $mr,
    branch: $branch,
    url: $url,
    vcs: $vcs,
    summary: {
      critical: $critical_count,
      warning: $warning_count,
      info: $info_count,
      human: $human_count,
      needs_fixes: (($critical_count + $warning_count + $human_count) > 0)
    },
    findings: {
      critical: $critical,
      warning: $warning,
      info: $info,
      human: $human
    }
  }'
