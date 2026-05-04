# Example workflow

**V1 workflow: Create Player and verify (`docs/workflow_v1_create_player.md`, aligned with `docs/api_specification.md`)**

**Goal.** Write a new NFL prospect in Postgres and verify the row with a reed.

**Steps**

1. **Create Player — `POST /players/`**  
   Insert one row with `name`, `position`, `college`, `draft_year`, `team`, `status`.  
   Successful response shape: `player_id` (string), `success` (boolean).

2. **Get Player by ID — `GET /players/{player_id}`**  
   Use the numeric `player_id` returned by step 1

---

# Testing results

After **POST**, replace `[PLAYER_ID]` with the `"player_id"` from that response._

## Step 1 — Create Player

**1.** The `curl` statement called:

```bash
curl -X 'POST' \
  '[BASE_URL]/players/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'access_token: [API_KEY]' \
  -d '{
  "name": "Example Prospect",
  "position": "WR",
  "college": "Cal Poly",
  "draft_year": 2026,
  "team": "FREE_AGENT",
  "status": "Prospect"
}'
```

**2.** The response received when executing that `curl` statement:

```json
REPLACE_WITH_RESPONSE_FROM_STEP_1
```

_Example of a successful payload shape your API returns:_

```json
{
  "player_id": "1",
  "success": true
}
```

---

## Step 2 — Get Player by ID

**1.** The `curl` statement called (`[PLAYER_ID]` = integer primary key returned as `player_id` in step 1):

```bash
curl -X 'GET' \
  '[BASE_URL]/players/[PLAYER_ID]' \
  -H 'accept: application/json' \
  -H 'access_token: [API_KEY]'
```

**2.** The response received when executing that `curl` statement:

```json
REPLACE_WITH_RESPONSE_FROM_STEP_2
```

_Example shape:_

```json
{
  "player_id": "1",
  "name": "Example Prospect",
  "position": "WR",
  "college": "Cal Poly",
  "draft_year": 2026,
  "team": "FREE_AGENT",
  "status": "Prospect"
}
```

