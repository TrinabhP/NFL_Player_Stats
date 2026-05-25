# Peer Review Response

We received feedback from three reviewers across issues #1-#12 on GitHub. Below is what we changed and our reasoning for anything we decided not to address.


## Jeanne Labuga (Issues #1, #2, #3, #4)

- Docs folder missing ER diagram and V2 workflow: not added for V4, our focus was on functionality and concurrency documentation.
- POST and PUT for combine stats should be merged: kept separate because they do different things. POST creates a new record and returns the new ID. PUT updates an existing one. Merging them adds upsert logic and makes the intent less clear.
- if statements in search should loop over params: left as-is. The explicit blocks are easier to read for a fixed set of fields.
- Endpoint naming, /players/create instead of POST /players/: not changed. POST /players/ is standard REST for resource creation.
- response_model missing on some endpoints: fixed. Added response models to GET /stats/top-performers/{event_name} and GET /stats/top-colleges/.
- Remove info.py: left as-is. It's a stub that isn't hurting anything.
- Handle duplicate players in POST /players/: not added. Name alone isn't a good uniqueness key since two players can share a name across different draft years.
- Invalid player_id handling: already works. All endpoints return 404 when a player isn't found.
- SQL injection risk in column interpolation: already safe. User values always use :param binding. Column names only come from constants we define in code and are never from user input.
- Players table quoting: the table is named with PascalCase so PostgreSQL requires quotes. Renaming it would mean rewriting every migration and query. Noted as tech debt.
- player_id should be int not str in Pydantic models: intentional. JavaScript can lose precision on 64-bit integers when parsing JSON, so we return IDs as strings to be safe.
- status should be an enum: not changed. Adding an enum requires a migration and could break existing data. We're keeping it as a free-form string for now.
- recorded_at in combine_stats is unnecessary: we disagree. It's a useful timestamp for knowing when data was entered and helps with debugging.
- GET /stats/top-performers should return event type: fixed. The response now includes event_name.
- Top combine stats and similar players as feature suggestions: both already exist as GET /stats/top-performers/{event_name} and GET /players/{player_id}/similar.


## Andy (Issues #5, #6, #10, #11)

- Test folder is empty: valid feedback. Not implemented by the V4 deadline.
- PUT /combine overwrites all fields: fixed. The endpoint now only updates the fields you actually send. If you send just forty_yard_dash, everything else stays the same.
- IDEAL_PLAYER_ID defined in admin.py but used in players.py: minor coupling, not worth refactoring for V4.
- GET /stats/top-colleges/ missing auth: fixed. Added API key dependency.
- GET /stats/top-colleges/ missing response_model: fixed.
- POST /players/ doesn't check for duplicates: not added. See reasoning above under Jeanne's feedback.
- POST /admin/reset should return a success boolean: the endpoint returns 204 No Content which is the correct HTTP response for an action with no body.
- Missing GET /players/ list endpoint: not added. GET /players/search/ already covers this with pagination. An unfiltered list could return thousands of rows.
- page_size should be a constant or query param: it's effectively a constant at 10. Making it a query param is a reasonable future improvement.
- Players table should be lowercase: same reasoning as above, noted as tech debt.
- Position, status, team should use enum constraints: same reasoning as above under Jeanne's feedback.
- Missing CHECK constraints on draft_year and measurements: would need a migration, not prioritized for V4.
- PUT requires full body, PATCH would be better: fixed as part of the partial update change.
- combine_stats.id is redundant since player_id is unique: the id column is consistent with every other table in the schema. Removing it requires a migration.
- Zero values in top-performers rankings: the query already filtered NULLs with IS NOT NULL. The real issue was the baseline player appearing. Fixed by excluding player_id = 1 from all stats queries.
- GET /players/compare and draft class composite rankings suggestions: good ideas, out of scope for V4.


## Leili Nelson (Issues #7, #8, #9, #12)

- Baseline player should be seeded in a migration not via reset: cleaner in theory but would require a new migration and changes to the reset endpoint. Not worth the risk for V4.
- Baseline player appearing in stats: fixed. Both position averages and top-performers now exclude player_id = 1.
- player_id string vs integer: same reasoning as above under Jeanne's feedback.
- Header comments for long files: not added. Function names and structure are descriptive enough.
- Error handling for player creation: already handled by the global SQLAlchemy exception handler in server.py.
- Migration optimization with server_default: those migrations have already run, retroactively changing them isn't practical.
- one_or_none() instead of first(): the two are functionally identical for unique-constrained columns. Not changed.
- SQL injection in get_top_performers: safe. event_name is validated against a whitelist before being used as a column reference.
- Extract helper functions from players.py: not done for V4. The helpers are closely tied to the player endpoints.
- anchor dict variable clarity: the name is already descriptive and a docstring exists on the function.
- New tables for colleges or teams: out of scope, too large a schema change for V4.
- Restructure combine endpoints to /combine/{player_id}: breaking API change, not worth it.
- Sort direction as boolean instead of asc/desc string: string direction is standard REST convention and already validated with a regex.
- Need endpoint to edit player attributes like team: valid gap. A PATCH /players/{player_id} endpoint would be the right addition but wasn't added for V4.
- Player deletion only possible via full reset: fixed. Added DELETE /players/{player_id}. Returns 204 on success, 404 if not found. Combine stats are removed automatically via cascade.
- Endpoint naming, position_avg vs positions: kept as positions/{position} for consistency with the rest of the stats router.
- Valid event_name examples missing from docs: noted, the valid values are listed in the API spec.
- Create an events table with FK constraints: not added. The VALID_EVENTS set in code does the same job without extra query overhead.
- status field meaning is unclear: status represents the player's roster situation such as DRAFTED, UNDRAFTED, or BASELINE.
- College should be nullable: a player without a college can use N/A. Not making it nullable.
- draft_year floor/ceiling constraints: would need a migration, not prioritized for V4.
- Team stats and historical combine stats suggestions: good ideas, out of scope for V4.
