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

# Workflow 2 — Statistical Insights

**Goal.** Add two more players with combine stats, then query position averages and top performers.

---

## Step 1 — Create Joe Croney (QB)

**1.** curl:

```bash
curl -X 'POST' \
  'http://127.0.0.1:3000/players/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'access_token: brat' \
  -d '{
  "name": "Joe Croney",
  "position": "QB",
  "college": "Cal Poly",
  "draft_year": 2026,
  "team": "Undrafted",
  "status": "Prospect"
}'
```

**2.** Response:

```json
{
  "player_id": "2",
  "success": true
}
```

---

## Step 2 — Add Combine Stats for Joe Croney

**1.** curl:

```bash
curl -X 'POST' \
  'http://127.0.0.1:3000/players/2/combine' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'access_token: brat' \
  -d '{
  "height_inches": 74.0,
  "weight_lbs": 210.0,
  "hand_size_inches": 9.5,
  "arm_length_inches": 32.0,
  "wingspan_inches": 76.0,
  "forty_yard_dash": 4.65,
  "ten_yard_split": 1.58,
  "twenty_yard_shuttle": 4.25,
  "three_cone": 7.05,
  "vertical_jump_inches": 32.0,
  "broad_jump_inches": 115.0,
  "bench_press_reps": 18
}'
```

**2.** Response:

```json
{
  "combine_id": "2",
  "success": true
}
```

---

## Step 3 — Create Trinabh Ponnapalli (LB)

**1.** curl:

```bash
curl -X 'POST' \
  'http://127.0.0.1:3000/players/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'access_token: brat' \
  -d '{
  "name": "Trinabh Ponnapalli",
  "position": "LB",
  "college": "Cal Poly",
  "draft_year": 2026,
  "team": "Undrafted",
  "status": "Prospect"
}'
```

**2.** Response:

```json
{
  "player_id": "3",
  "success": true
}
```

---

## Step 4 — Add Combine Stats for Trinabh Ponnapalli

**1.** curl:

```bash
curl -X 'POST' \
  'http://127.0.0.1:3000/players/3/combine' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'access_token: brat' \
  -d '{
  "height_inches": 72.0,
  "weight_lbs": 225.0,
  "hand_size_inches": 9.75,
  "arm_length_inches": 32.5,
  "wingspan_inches": 77.0,
  "forty_yard_dash": 4.52,
  "ten_yard_split": 1.54,
  "twenty_yard_shuttle": 4.20,
  "three_cone": 6.88,
  "vertical_jump_inches": 37.0,
  "broad_jump_inches": 122.0,
  "bench_press_reps": 25
}'
```

**2.** Response:

```json
{
  "combine_id": "3",
  "success": true
}
```

---

## Step 5 — Position Averages for WR

**1.** curl:

```bash
curl -X 'GET' \
  'http://127.0.0.1:3000/stats/positions/WR' \
  -H 'accept: application/json' \
  -H 'access_token: brat'
```

**2.** Response:

```json
{
  "position": "WR",
  "averages": {
    "height_inches": 73.0,
    "weight_lbs": 195.0,
    "forty_yard_dash": 4.41,
    "vertical_jump_inches": 35.0,
    "broad_jump_inches": 120.0,
    "bench_press_reps": 12.0,
    "three_cone": 6.92,
    "twenty_yard_shuttle": 4.18
  }
}
```

---

## Step 6 — Top Performers by 40-yard Dash

**1.** curl:

```bash
curl -X 'GET' \
  'http://127.0.0.1:3000/stats/top-performers/forty_yard_dash?limit=3' \
  -H 'accept: application/json' \
  -H 'access_token: brat'
```

**2.** Response:

```json
[
  {
    "player_id": "1",
    "name": "Caleb So",
    "position": "WR",
    "draft_year": 2026,
    "value": 4.41
  },
  {
    "player_id": "3",
    "name": "Trinabh Ponnapalli",
    "position": "LB",
    "draft_year": 2026,
    "value": 4.52
  },
  {
    "player_id": "2",
    "name": "Joe Croney",
    "position": "QB",
    "draft_year": 2026,
    "value": 4.65
  }
]
```