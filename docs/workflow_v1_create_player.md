# V1 example workflow — Create Player (from API specification)

This workflow is scoped to **[§1 Player and Combine Data Management](/docs/api_specification.md)** in `api_specification.md`. It follows the documented call order (“Create a new Player” first, then “Get a player by ID”).

**Goal.** A client adds one new NFL prospect record so it is persisted in the database (**write**).

---

## Workflow steps

### Step 1 — Create Player

- **Purpose.** Insert a new player row
- **Method & path.** `POST /players/` 

**Request body** (shape from the spec; replace values with real data):

| Field         | Type    | Meaning (per spec)   |
|--------------|---------|----------------------|
| `name`       | string  | Player name          |
| `position`   | string  | Playing position      |
| `college`    | string  | College              |
| `draft_year` | integer | Draft year           |
| `team`       | string  | Team                 |
| `status`     | string  | Status               |

**Expected success response shape** (per spec):

- `player_id` (string): identifier for the new row  
- `success` (boolean): indicates whether creation succeeded  

### Step 2 — Get Player by ID (verification)

- **Purpose.** Confirm the row exists and matches what was submitted 

- **Method & path.** `GET /players/{player_id}`

**Expected response shape**: full player profile — same fields as listed for the GET response (`player_id`, `name`, `position`, `college`, `draft_year`, `team`, `status`)

