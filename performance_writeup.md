# Performance Writeup

---

## 1. Fake Data Modeling

**Python script:** [populate.py](populate.py)

### Row counts

| Table | Rows |
|---|---|
| `Players` | 700,000 |
| `combine_stats` | 300,000 |
| **Total** | **1,000,000** |

### Justification

This service tracks every player who has ever been formally evaluated by professional football scouts, starting with the introduction of organized multi-team scouting networks in 1967 through the 2025 season. Coverage includes:

- **NFL Combine invitees** (~300 per year, post-1982)
- **Regional scouting combine participants** (~500–800 per year through organizations like BLESTO and National Football Scouting)
- **Pro Day participants** (~1,200–2,000 per year at NCAA programs)
- **FCS, D2, D3, and HBCU prospects** formally evaluated by at least one scout (~5,000–10,000 per year in the modern era)

The **700,000-player count** works out to roughly 11,900 prospects per year across 59 years (1967–2025). This is conservative: modern NFL scouting organizations evaluate upwards of 15,000 players per year when smaller programs are included, and historical records accumulated since 1967 bring the total into seven-figure territory. The triangular distribution used in `populate.py` (low=1967, high=2025, mode=2010) skews the data toward recent draft years, reflecting the explosive growth of advanced analytics and digital scouting platforms that digitized records starting in the late 2000s.

Of 700,000 players, **300,000 (~43%) have combine_stats rows**. The combine is a formal event requiring invitations, not attended by all prospects. Pre-1990 records are sparse; many players from that era were evaluated via scouts' notes rather than measured events. Post-2010 players trend toward 60–70% formal measurement coverage. The 43% overall rate is pulled down by the large historical base where formal measurements were rarely recorded.

**Position distribution** mirrors approximate real-world NFL draft rates (WR 12%, LB/CB 10% each, RB/DE 9% each, OT 8%, TE/S 7% each, QB/OG 6% each, C 4%, K/P 2% each). **65% of players are on a team** (status DRAFTED/ACTIVE/RETIRED), with 35% UNDRAFTED, reflecting the large pool of prospects who were evaluated but never signed.

---

## 2. Performance Results of Hitting Endpoints

*Run the server against local Postgres after populate.py completes. Time each request end-to-end using `curl -o /dev/null -s -w "%{time_total}s\n"` or the `/docs` UI.*

| Endpoint | Method | Sample Parameters | Time (ms) |
|---|---|---|---|
| `GET /players/{player_id}` | GET | player_id=2 | |
| `DELETE /players/{player_id}` | DELETE | player_id=2 | |
| `POST /players/` | POST | new player body | |
| `GET /players/search/` | GET | no filters | |
| `GET /players/search/` | GET | position=WR, sort_col=forty_yard_dash | |
| `GET /players/{player_id}/similar` | GET | player_id=2, limit=10 | |
| `GET /players/{player_id}/similar` | GET | player_id=2, position_only=true | |
| `GET /players/{player_id}/prediction` | GET | player_id=2 | |
| `GET /stats/positions/{position}` | GET | position=QB | |
| `GET /stats/top-performers/{event}` | GET | event=forty_yard_dash | |
| `GET /stats/top-colleges/` | GET | — | |
| `GET /info/summary` | GET | — | |

**Slowest endpoint:** `GET /players/{player_id}/similar`

This endpoint fetches all ~300,000 combine_stats rows into Python memory, then runs 300,000 pairwise similarity computations, then sorts in Python — O(n) DB I/O plus O(n log n) CPU-side work, all in one request.

---

## 3. Performance Tuning

### Slowest endpoint: `GET /players/{player_id}/similar`

The core query inside `_fetch_similarity_candidates` (players.py:306–323):

```sql
SELECT
    p.id, p.name, p.position, p.team, p.draft_year,
    c.height_inches, c.weight_lbs, c.hand_size_inches,
    c.arm_length_inches, c.wingspan_inches, c.forty_yard_dash,
    c.ten_yard_split, c.twenty_yard_shuttle, c.three_cone,
    c.vertical_jump_inches, c.broad_jump_inches, c.bench_press_reps
FROM "Players" p
INNER JOIN combine_stats c ON c.player_id = p.id
WHERE p.id != :exclude_player_id
```

With optional filters:
```sql
  AND LOWER(p.position) = LOWER(:required_position)   -- when position_only=true
  AND p.draft_year >= :draft_year_min
  AND p.draft_year <= :draft_year_max
```

### EXPLAIN ANALYZE output (before any new indexes)

```
-- Run this in psql while the server is pointing at your local DB:
EXPLAIN ANALYZE
SELECT p.id, p.name, p.position, p.team, p.draft_year,
       c.height_inches, c.weight_lbs, c.hand_size_inches,
       c.arm_length_inches, c.wingspan_inches, c.forty_yard_dash,
       c.ten_yard_split, c.twenty_yard_shuttle, c.three_cone,
       c.vertical_jump_inches, c.broad_jump_inches, c.bench_press_reps
FROM "Players" p
INNER JOIN combine_stats c ON c.player_id = p.id
WHERE p.id != 2;

[paste EXPLAIN ANALYZE output here]
```

### What the EXPLAIN output shows

*Fill in after running EXPLAIN. Look for:*
- **Seq Scan on combine_stats** — no useful index for the join or position filter
- **Seq Scan on "Players"** — no index filtering by position/draft_year
- **Hash Join** — likely the join strategy with 300K rows
- Estimated vs actual rows — check if the planner is off

*The two main sources of slowness are:*
1. **Full table scan**: every combine_stats row (300K) must be read from disk regardless of filters.
2. **Python-side computation**: all 300K rows are fetched into Python for pairwise similarity; no work is pushed into SQL.

### Index 1 — speed up position_only filter

When `position_only=true` the query adds `LOWER(p.position) = LOWER(:required_position)`, which currently requires a sequential scan of Players. A functional index on the lowercased position column lets Postgres use an index scan and dramatically reduces the number of Players rows that need to be joined.

```sql
CREATE INDEX idx_players_position_lower
ON "Players" (LOWER(position));
```

### EXPLAIN ANALYZE after index 1

```sql
[paste EXPLAIN ANALYZE output here after adding the index]
```

### Index 2 — speed up draft_year range filters

The `draft_year_min` / `draft_year_max` filters scan all Players rows without an index. A plain B-tree index enables range scans.

```sql
CREATE INDEX idx_players_draft_year
ON "Players" (draft_year);
```

### EXPLAIN ANALYZE after index 2

```sql
[paste EXPLAIN ANALYZE output here after adding the index]
```

### Index 3 — speed up the search endpoint join

`GET /players/search/` does a LEFT JOIN between Players and combine_stats filtered by several columns. The existing UNIQUE constraint on `combine_stats.player_id` already creates an index for the join, but a partial or composite index can help when filtering on combine stat columns (min_forty, max_forty, etc.).

```sql
CREATE INDEX idx_combine_forty_bench
ON combine_stats (forty_yard_dash, bench_press_reps);
```

### Final EXPLAIN ANALYZE

```sql
[paste final EXPLAIN ANALYZE output here]
```

### Result

*Describe whether execution time reached an acceptable level and, if not, what additional tuning was done.*
