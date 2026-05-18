---
name: jira-integration
description: Use this skill when interacting with Jira — fetching issues, searching with JQL, transitioning status, or adding comments. Triggers include Jira issue keys (e.g., FOC-12345, MDI-100), requests to look up/update/close tickets, or checking acceptance criteria from Jira. On-prem Jira Server with Bearer PAT auth and REST API v2.
---

# Jira Integration (On-Prem)

Interact with the on-prem Jira Server instance using `curl` with Bearer token authentication.

## Environment

Three env vars must be set (injected via Ona secrets in `/etc/environment`):

| Variable | Purpose |
|----------|---------|
| `ATLASSIAN_TOKEN` | Personal Access Token (Bearer auth) |
| `ATLASSIAN_DOMAIN` | Jira hostname (e.g., `globaljira.roche.com`) |
| `ATLASSIAN_EMAIL` | Account email (informational, not used for auth) |

## Auth Pattern

All requests use Bearer token auth against REST API v2:

```bash
curl -s -H "Authorization: Bearer $ATLASSIAN_TOKEN" \
  "https://${ATLASSIAN_DOMAIN}/rest/api/2/..."
```

**Do not use** Basic auth (`email:token` base64) — it does not work on this on-prem instance.

---

## Operations

### 1. Get Issue

Fetch a single issue by key:

```bash
curl -s -H "Authorization: Bearer $ATLASSIAN_TOKEN" \
  "https://${ATLASSIAN_DOMAIN}/rest/api/2/issue/FOC-11952?fields=summary,status,assignee,priority,description" \
  | python3 -m json.tool
```

Common field selections:
- Minimal: `?fields=summary,status`
- Standard: `?fields=summary,status,assignee,priority,labels`
- Full: omit `fields` parameter

### 2. JQL Search

Search issues using JQL:

```bash
curl -s -H "Authorization: Bearer $ATLASSIAN_TOKEN" \
  --get --data-urlencode "jql=project = FOC AND status = 'In Progress'" \
  --data-urlencode "fields=summary,status,assignee" \
  --data-urlencode "maxResults=20" \
  "https://${ATLASSIAN_DOMAIN}/rest/api/2/search" \
  | python3 -m json.tool
```

Useful JQL patterns:
- `project = FOC AND status = 'Build In Progress'`
- `project = FOC AND sprint in openSprints()`
- `assignee = currentUser() AND status != Done`
- `issuekey in (FOC-11952, FOC-10727)`

Results are in `.issues[]` array. Pagination via `startAt` and `maxResults`.

### 3. Transition Issue (Change Status)

Two-step process — first get available transitions, then apply one:

**Step 1: Get transitions**
```bash
curl -s -H "Authorization: Bearer $ATLASSIAN_TOKEN" \
  "https://${ATLASSIAN_DOMAIN}/rest/api/2/issue/FOC-11952/transitions" \
  | python3 -c "import sys,json; [print(f'{t[\"id\"]}: {t[\"name\"]} -> {t[\"to\"][\"name\"]}') for t in json.load(sys.stdin)['transitions']]"
```

**Step 2: Apply transition**
```bash
curl -s -w "\nHTTP_STATUS: %{http_code}\n" -X POST \
  -H "Authorization: Bearer $ATLASSIAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"transition":{"id":"41"}}' \
  "https://${ATLASSIAN_DOMAIN}/rest/api/2/issue/FOC-11952/transitions"
```

A successful transition returns HTTP 204 with no body.

### 4. Add Comment

```bash
curl -s -X POST \
  -H "Authorization: Bearer $ATLASSIAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"body":"Your comment text here"}' \
  "https://${ATLASSIAN_DOMAIN}/rest/api/2/issue/FOC-11952/comment" \
  | python3 -m json.tool
```

A successful comment returns HTTP 201 with the created comment object.

For multi-line comments, use a variable:

```bash
COMMENT="Line one.
Line two.
Line three."
curl -s -X POST \
  -H "Authorization: Bearer $ATLASSIAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"body\": $(echo "$COMMENT" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')}" \
  "https://${ATLASSIAN_DOMAIN}/rest/api/2/issue/FOC-11952/comment"
```

---

## Error Handling

| HTTP Status | Meaning |
|-------------|---------|
| 200/201 | Success |
| 204 | Success (no body, e.g., transitions) |
| 401 | Token expired or invalid — user needs to regenerate PAT |
| 403 | Permission denied for this operation |
| 404 | Issue not found |

If you get 401, tell the user their `ATLASSIAN_TOKEN` may need regeneration in Jira: **Profile > Personal Access Tokens > Create token**, then update in Ona secrets and rebuild the dev container.
