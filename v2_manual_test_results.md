# V2 Manual Test Results

All calls run against the local server on port 3000 (`python main.py`) with header `access_token: brat`.

---

# Workflow 1 — Combine Stats Lifecycle

**Goal.** Create a player, attach combine stats, verify them, update one field, then verify the update.

---

## Step 1 — Create Player

**1.** curl:

```bash
curl -X 'POST' \
  'http://127.0.0.1:3000/players/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'access_token: brat' \
  -d '{
  "name": "Caleb So",
  "position": "WR",
  "college": "Cal Poly",
  "draft_year": 2026,
  "team": "Undrafted",
  "status": "Prospect"
}'
```

**2.** Response:

```json
{
  "player_id": "1",
  "success": true
}
```

---

## Step 2 — Add Combine Stats

**1.** curl:

```bash
curl -X 'POST' \
  'http://127.0.0.1:3000/players/1/combine' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'access_token: brat' \
  -d '{
  "height_inches": 73.0,
  "weight_lbs": 195.0,
  "hand_size_inches": 9.25,
  "arm_length_inches": 31.5,
  "wingspan_inches": 75.0,
  "forty_yard_dash": 4.55,
  "ten_yard_split": 1.55,
  "twenty_yard_shuttle": 4.18,
  "three_cone": 6.92,
  "vertical_jump_inches": 35.0,
  "broad_jump_inches": 120.0,
  "bench_press_reps": 12
}'
```

**2.** Response:

```json
{
  "combine_id": "1",
  "success": true
}
```

---

## Step 3 — Get Combine Stats

**1.** curl:

```bash
curl -X 'GET' \
  'http://127.0.0.1:3000/players/1/combine' \
  -H 'accept: application/json' \
  -H 'access_token: brat'
```

**2.** Response:

```json
{
  "player_id": "1",
  "name": "Caleb So",
  "position": "WR",
  "combine_stats": {
    "height_inches": 73.0,
    "weight_lbs": 195.0,
    "hand_size_inches": 9.25,
    "arm_length_inches": 31.5,
    "wingspan_inches": 75.0,
    "forty_yard_dash": 4.55,
    "ten_yard_split": 1.55,
    "twenty_yard_shuttle": 4.18,
    "three_cone": 6.92,
    "vertical_jump_inches": 35.0,
    "broad_jump_inches": 120.0,
    "bench_press_reps": 12
  }
}
```

---

## Step 4 — Update Combine Stats (correct 40-yard dash)

**1.** curl:

```bash
curl -X 'PUT' \
  'http://127.0.0.1:3000/players/1/combine' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'access_token: brat' \
  -d '{
  "height_inches": 73.0,
  "weight_lbs": 195.0,
  "hand_size_inches": 9.25,
  "arm_length_inches": 31.5,
  "wingspan_inches": 75.0,
  "forty_yard_dash": 4.41,
  "ten_yard_split": 1.55,
  "twenty_yard_shuttle": 4.18,
  "three_cone": 6.92,
  "vertical_jump_inches": 35.0,
  "broad_jump_inches": 120.0,
  "bench_press_reps": 12
}'
```

**2.** Response:

```json
{
  "success": true
}
```

---

## Step 5 — Verify Update

**1.** curl:

```bash
curl -X 'GET' \
  'http://127.0.0.1:3000/players/1/combine' \
  -H 'accept: application/json' \
  -H 'access_token: brat'
```

**2.** Response (`forty_yard_dash` updated from 4.55 to 4.41):

```json
{
  "player_id": "1",
  "name": "Caleb So",
  "position": "WR",
  "combine_stats": {
    "height_inches": 73.0,
    "weight_lbs": 195.0,
    "hand_size_inches": 9.25,
    "arm_length_inches": 31.5,
    "wingspan_inches": 75.0,
    "forty_yard_dash": 4.41,
    "ten_yard_split": 1.55,
    "twenty_yard_shuttle": 4.18,
    "three_cone": 6.92,
    "vertical_jump_inches": 35.0,
    "broad_jump_inches": 120.0,
    "bench_press_reps": 12
  }
}
```
