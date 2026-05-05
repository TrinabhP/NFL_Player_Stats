# Example workflow

**V1 workflow: Create Player and verify**

**Goal.** Write a new NFL prospect in Postgres (**write**) and verify the row with a **read**

**Steps**

1. **Create Player — `POST /players/`**  
   Insert one row with `name`, `position`, `college`, `draft_year`, `team`, `status`
   Successful response includes `player_id` (string) and `success` (boolean)

2. **Get Player by ID — `GET /players/{player_id}`**  
   Use the `player_id` from step 1 as the path segment

**Auth.** Both calls use header `access_token` equal to `API_KEY` (eg `brat` from `default.env` for local testing)

---

# Testing results

Below is a sample local run on port 3000 (`python main.py`)
each step lists (1) the `curl` used and (2) the response observed.

## Step 1 — Create Player

**1.** The `curl` statement called:

```bash
curl -X 'POST' \
  'http://127.0.0.1:3000/players/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'access_token: brat' \
  -d '{
  "name": "Peter Moschitto",
  "position": "WR",
  "college": "Cal Poly",
  "draft_year": 2026,
  "team": "San Francisco 49ers",
  "status": "Prospect"
}'
```

**2.** The response received when executing that `curl` statement:

```json
{
  "player_id": "1",
  "success": true
}
```

---

## Step 2 — Get Player by ID

**1.** The `curl` statement called (use the id returned in step 1; here `1`):

```bash
curl -X 'GET' \
  'http://127.0.0.1:3000/players/1' \
  -H 'accept: application/json' \
  -H 'access_token: brat'
```

**2.** The response received when executing that `curl` statement:

```json
{
  "player_id": "1",
  "name": "Peter Moschitto",
  "position": "WR",
  "college": "Cal Poly",
  "draft_year": 2026,
  "team": "San Francisco 49ers",
  "status": "Prospect"
}
```
