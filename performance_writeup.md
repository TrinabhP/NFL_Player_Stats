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
| `GET /players/{player_id}` | GET | player_id=2 | 12.00 ms |
| `DELETE /players/{player_id}` | DELETE | player_id=2 | 15.70 ms |
| `POST /players/` | POST | new player body | 9.81 ms |
| `GET /players/search/` | GET | no filters | 190.65 ms |
| `GET /players/search/` | GET | position=WR, sort_col=forty_yard_dash | 155.64 ms |
| `GET /players/{player_id}/similar` | GET | player_id=2, limit=10 | 11001.46 ms |
| `GET /players/{player_id}/similar` | GET | player_id=2, position_only=true | 95.03 ms |
| `GET /players/{player_id}/prediction` | GET | player_id=2 | 5.82 ms |
| `GET /stats/positions/{position}` | GET | position=QB | 118.65 ms |
| `GET /stats/top-performers/{event}` | GET | event=forty_yard_dash | 42.52 ms |
| `GET /stats/top-colleges/` | GET | — | 81.18 ms |
| `GET /info/summary` | GET | — | 0.79 ms |

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

Explain Analyze Output:

```sql
Merge Join  (cost=3.85..46449.57 rows=300002 width=99) (actual time=0.097..319.487 rows=300001.00 loops=1)
  Merge Cond: (p.id = c.player_id)
  Buffers: shared hit=15951
"  ->  Index Scan using ""Players_pkey"" on ""Players"" p  (cost=0.42..28290.46 rows=700001 width=28) (actual time=0.053..168.406 rows=700001.00 loops=1)"
        Filter: (id <> 2)
        Rows Removed by Filter: 1
        Index Searches: 1
        Buffers: shared hit=10290
  ->  Index Scan using combine_stats_player_id_key on combine_stats c  (cost=0.42..12660.45 rows=300002 width=75) (actual time=0.036..75.744 rows=300002.00 loops=1)
        Index Searches: 1
        Buffers: shared hit=5661
Planning:
  Buffers: shared hit=16
Planning Time: 1.064 ms
Execution Time: 328.553 ms
```

### What the EXPLAIN output shows

- **Merge Join**, not a hash join — Postgres merges two index-ordered streams on `p.id = c.player_id`.
- **Index Scan on `Players_pkey`** — walks all ~700K player rows and applies `id <> 2` as a filter (removes 1 row). No position or draft-year predicate is present, so none of the new indexes can be used here.
- **Index Scan on `combine_stats_player_id_key`** — reads all ~300K combine rows via the existing unique constraint index. There are no sequential scans on either table.
- **Row estimates are accurate** — planner predicted ~300K rows; actual count is 300,001.
- **~329 ms execution time**, with all buffers served from cache (`shared hit=15951`).

The bottleneck is **row volume**, not a missing join index. This query always materializes nearly every combine_stats row. The optional filters (`position_only`, draft-year range) are what would benefit from Indexes 1 and 2, but the baseline EXPLAIN above does not include them.

The endpoint remains slow overall because:
1. **~300K rows are returned to the application** on every similar-player request (with default filters).
2. **Similarity scoring and sorting happen in Python** — O(n) comparisons plus O(n log n) sort — which dominates end-to-end latency beyond the ~250–330 ms DB time.

### Index 1 — speed up position_only filter

When `position_only=true` the query adds `LOWER(p.position) = LOWER(:required_position)`, which currently requires a sequential scan of Players. A functional index on the lowercased position column lets Postgres use an index scan and dramatically reduces the number of Players rows that need to be joined.

```sql
CREATE INDEX idx_players_position_lower
ON "Players" (LOWER(position));
```

### EXPLAIN ANALYZE after index 1

```sql
Merge Join  (cost=3.85..46449.57 rows=300002 width=99) (actual time=0.139..274.845 rows=300001.00 loops=1)
  Merge Cond: (p.id = c.player_id)
  Buffers: shared hit=15951
"  ->  Index Scan using ""Players_pkey"" on ""Players"" p  (cost=0.42..28290.46 rows=700001 width=28) (actual time=0.084..144.176 rows=700001.00 loops=1)"
        Filter: (id <> 2)
        Rows Removed by Filter: 1
        Index Searches: 1
        Buffers: shared hit=10290
  ->  Index Scan using combine_stats_player_id_key on combine_stats c  (cost=0.42..12660.45 rows=300002 width=75) (actual time=0.049..60.363 rows=300002.00 loops=1)
        Index Searches: 1
        Buffers: shared hit=5661
Planning:
  Buffers: shared hit=16
Planning Time: 1.662 ms
Execution Time: 283.338 ms
```

### Index 2 — speed up draft_year range filters

The `draft_year_min` / `draft_year_max` filters scan all Players rows without an index. A plain B-tree index enables range scans.

```sql
CREATE INDEX idx_players_draft_year
ON "Players" (draft_year);
```

### EXPLAIN ANALYZE after index 2

```sql
Merge Join  (cost=3.85..46449.57 rows=300002 width=99) (actual time=0.083..279.440 rows=300001.00 loops=1)
  Merge Cond: (p.id = c.player_id)
  Buffers: shared hit=15951
"  ->  Index Scan using ""Players_pkey"" on ""Players"" p  (cost=0.42..28290.46 rows=700001 width=28) (actual time=0.051..148.062 rows=700001.00 loops=1)"
        Filter: (id <> 2)
        Rows Removed by Filter: 1
        Index Searches: 1
        Buffers: shared hit=10290
  ->  Index Scan using combine_stats_player_id_key on combine_stats c  (cost=0.42..12660.45 rows=300002 width=75) (actual time=0.028..59.376 rows=300002.00 loops=1)
        Index Searches: 1
        Buffers: shared hit=5661
Planning:
  Buffers: shared hit=16
Planning Time: 0.996 ms
Execution Time: 288.370 ms
```

### Index 3 — speed up the search endpoint join

`GET /players/search/` does a LEFT JOIN between Players and combine_stats filtered by several columns. The existing UNIQUE constraint on `combine_stats.player_id` already creates an index for the join, but a partial or composite index can help when filtering on combine stat columns (min_forty, max_forty, etc.).

```sql
CREATE INDEX idx_combine_forty_bench
ON combine_stats (forty_yard_dash, bench_press_reps);
```

### Final EXPLAIN ANALYZE

```sql
Merge Join  (cost=3.85..46449.57 rows=300002 width=99) (actual time=0.079..246.564 rows=300001.00 loops=1)
  Merge Cond: (p.id = c.player_id)
  Buffers: shared hit=15951
"  ->  Index Scan using ""Players_pkey"" on ""Players"" p  (cost=0.42..28290.46 rows=700001 width=28) (actual time=0.048..126.545 rows=700001.00 loops=1)"
        Filter: (id <> 2)
        Rows Removed by Filter: 1
        Index Searches: 1
        Buffers: shared hit=10290
  ->  Index Scan using combine_stats_player_id_key on combine_stats c  (cost=0.42..12660.45 rows=300002 width=75) (actual time=0.027..52.749 rows=300002.00 loops=1)
        Index Searches: 1
        Buffers: shared hit=5661
Planning:
  Buffers: shared hit=16
Planning Time: 0.817 ms
Execution Time: 254.458 ms
```

### Result

Adding all three indexes did not materially change the plan for the unfiltered similar players query — execution time moved from ~329 ms (baseline) to ~254 ms (final), within normal run to run variance. The plan still uses `Players_pkey` and `combine_stats_player_id_key`; none of the new indexes appear because the test query lacks position and draft year predicates, and Index 3 targets the search endpoint rather than this one.

The indexes are still worthwhile for filtered calls: `idx_players_position_lower` should reduce rows when `position_only=true`, and `idx_players_draft_year` should help draft year range filters. `idx_combine_forty_bench` may improve `GET /players/search/` when filtering on forty yard dash or bench press.

**Verdict:** DB query time (~250–330 ms) is reasonable for returning 300K rows, but the endpoint is still the slowest because the application fetches and scores every candidate in Python. Indexes alone do not make `/similar` acceptably fast at full scale. Meaningful further gains would require pushing work into SQL (e.g., limiting candidates before fetch), pre filtering aggressively, or replacing the brute force similarity loop with a smaller candidate set or approximate nearest-neighbor approach.
