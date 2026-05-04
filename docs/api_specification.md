# API Specification for NFL Player Combine Stats and Predictions

## 1. Player and Combine Data Management

The API calls are typically made in this sequence when entering and viewing player data:

## 1. Create a new Player

## 2. Get a player by ID

## 3. Search Players (filters)

## 4. Update Player Stats

## 5. Delete a Player

## 6. Compare Players

## 7. Find Similar Players

## 8. Aggregate Stats

## 9. Find Best Colleges that Produce Most NFL Prospects

Get Players
Create Player
Add Combine Stats
Get Player Combine Stats
Compare Player to Similar Players
Get Prediction
1.1. Get Players - /players/ (GET)

Retrieves all players currently stored in the system.

Query Parameters:

name (optional): Filter by player name
position (optional): Filter by position
college (optional): Filter by college
draft_year (optional): Filter by draft year
limit (optional): Maximum number of players returned
offset (optional): Pagination offset

Response:

[
  {
    "player_id": "string",
    "name": "string",
    "position": "string",
    "college": "string",
    "draft_year": "integer",
    "team": "string",
    "status": "string"
  }
]
1.2. Create Player - /players/ (POST)

Creates a new player entry in the database.

Request:

{
  "name": "string",
  "position": "string",
  "college": "string",
  "draft_year": "integer",
  "team": "string",
  "status": "string"
}

Response:

{
  "player_id": "string",
  "success": "boolean"
}
1.3. Get Player by ID - /players/{player_id} (GET)

Retrieves detailed information for one specific player.

Response:

{
  "player_id": "string",
  "name": "string",
  "position": "string",
  "college": "string",
  "draft_year": "integer",
  "team": "string",
  "status": "string"
}
1.4. Add Combine Stats - /players/{player_id}/combine (POST)

Adds combine performance stats for a specific player.

Request:

{
  "height_inches": "number",
  "weight_lbs": "number",
  "hand_size_inches": "number",
  "arm_length_inches": "number",
  "wingspan_inches": "number",
  "forty_yard_dash": "number",
  "ten_yard_split": "number",
  "twenty_yard_shuttle": "number",
  "three_cone": "number",
  "vertical_jump_inches": "number",
  "broad_jump_inches": "number",
  "bench_press_reps": "integer"
}

Response:

{
  "combine_id": "string",
  "success": "boolean"
}
1.5. Update Combine Stats - /players/{player_id}/combine (PUT)

Updates an existing combine stats record for a player.

Request:

{
  "height_inches": "number",
  "weight_lbs": "number",
  "hand_size_inches": "number",
  "arm_length_inches": "number",
  "wingspan_inches": "number",
  "forty_yard_dash": "number",
  "ten_yard_split": "number",
  "twenty_yard_shuttle": "number",
  "three_cone": "number",
  "vertical_jump_inches": "number",
  "broad_jump_inches": "number",
  "bench_press_reps": "integer"
}

Response:

{
  "success": "boolean"
}
1.6. Get Player Combine Stats - /players/{player_id}/combine (GET)

Retrieves combine stats for a specific player.

Response:

{
  "player_id": "string",
  "name": "string",
  "position": "string",
  "combine_stats": {
    "height_inches": "number",
    "weight_lbs": "number",
    "hand_size_inches": "number",
    "arm_length_inches": "number",
    "wingspan_inches": "number",
    "forty_yard_dash": "number",
    "ten_yard_split": "number",
    "twenty_yard_shuttle": "number",
    "three_cone": "number",
    "vertical_jump_inches": "number",
    "broad_jump_inches": "number",
    "bench_press_reps": "integer"
  }
}
1.7. Delete Player - /players/{player_id} (DELETE)

Deletes a player and associated combine stats from the system.

Response:

{
  "success": "boolean"
}
2. Similar Player Analysis

The API calls are typically made in this sequence when comparing a player:

Get Player Combine Stats
Compare Player to Similar Players
Get Prediction
2.1. Compare Player to Similar Players - /players/{player_id}/similar (GET)

Finds players in the database with combine stats and attributes most similar to the selected player.

Query Parameters:

limit (optional): Number of similar players to return
position_only (optional): If true, only compares players at the same position
draft_year_min (optional): Minimum draft year to consider
draft_year_max (optional): Maximum draft year to consider

Response:

{
  "player_id": "string",
  "name": "string",
  "position": "string",
  "similar_players": [
    {
      "player_id": "string",
      "name": "string",
      "position": "string",
      "team": "string",
      "draft_year": "integer",
      "similarity_score": "number"
    }
  ]
}
2.2. Get Prediction - /players/{player_id}/prediction (GET)

Returns a prediction for how successful a player may be based on combine results and similarity to other NFL players.

Response:

{
  "player_id": "string",
  "name": "string",
  "position": "string",
  "prediction": {
    "success_score": "number",
    "success_tier": "string",
    "projected_outcome": "string",
    "confidence": "number"
  },
  "based_on": [
    {
      "player_id": "string",
      "name": "string",
      "similarity_score": "number"
    }
  ]
}
2.3. Predict from Raw Stats - /predictions/ (POST)

Creates a prediction without first creating a saved player record. Useful for testing a new prospect.

Request:

{
  "name": "string",
  "position": "string",
  "college": "string",
  "draft_year": "integer",
  "combine_stats": {
    "height_inches": "number",
    "weight_lbs": "number",
    "hand_size_inches": "number",
    "arm_length_inches": "number",
    "wingspan_inches": "number",
    "forty_yard_dash": "number",
    "ten_yard_split": "number",
    "twenty_yard_shuttle": "number",
    "three_cone": "number",
    "vertical_jump_inches": "number",
    "broad_jump_inches": "number",
    "bench_press_reps": "integer"
  }
}

Response:

{
  "prediction": {
    "success_score": "number",
    "success_tier": "string",
    "projected_outcome": "string",
    "confidence": "number"
  },
  "similar_players": [
    {
      "player_id": "string",
      "name": "string",
      "position": "string",
      "draft_year": "integer",
      "similarity_score": "number"
    }
  ]
}
3. Search and Filtering
3.1. Search Players - /players/search/ (GET)

Searches for players based on specified query parameters.

Query Parameters:

name (optional): Player name
position (optional): Position
college (optional): College
team (optional): Team
draft_year (optional): Draft year
min_forty (optional): Minimum 40-yard dash time
max_forty (optional): Maximum 40-yard dash time
min_bench (optional): Minimum bench press reps
max_bench (optional): Maximum bench press reps
search_page (optional): Page number
sort_col (optional): Column to sort by. Possible values: name, position, draft_year, forty_yard_dash, bench_press_reps
sort_order (optional): asc or desc

Response:

{
  "previous": "string",
  "next": "string",
  "results": [
    {
      "player_id": "string",
      "name": "string",
      "position": "string",
      "college": "string",
      "draft_year": "integer",
      "team": "string",
      "forty_yard_dash": "number",
      "bench_press_reps": "integer"
    }
  ]
}
4. Statistical Insights
4.1. Get Position Averages - /stats/positions/{position} (GET)

Returns average combine stats for players at a given position.

Response:

{
  "position": "string",
  "averages": {
    "height_inches": "number",
    "weight_lbs": "number",
    "forty_yard_dash": "number",
    "vertical_jump_inches": "number",
    "broad_jump_inches": "number",
    "bench_press_reps": "number",
    "three_cone": "number",
    "twenty_yard_shuttle": "number"
  }
}
4.2. Get Top Performers by Event - /stats/top-performers/{event_name} (GET)

Returns the best performers in a specific combine event.

Path Parameters:

event_name: one of forty_yard_dash, bench_press_reps, vertical_jump_inches, broad_jump_inches, three_cone, twenty_yard_shuttle

Query Parameters:

limit (optional): Number of results to return
position (optional): Filter by position

Response:

[
  {
    "player_id": "string",
    "name": "string",
    "position": "string",
    "draft_year": "integer",
    "value": "number"
  }
]
5. Admin Functions
5.1. Reset Database - /admin/reset (POST)

Resets the application by clearing all players, combine stats, and predictions.

Response:

{
  "success": "boolean"
}
5.2. Seed Sample Data - /admin/seed (POST)

Loads the database with sample NFL combine data for testing and development.

Response:

{
  "players_inserted": "integer",
  "combine_records_inserted": "integer",
  "success": "boolean"
}
6. Audit / Info Functions
6.1. Get Database Summary - /info/summary (GET)

Returns a summary of the current contents of the system.

Response:

{
  "total_players": "integer",
  "total_combine_records": "integer",
  "total_predictions_generated": "integer",
  "last_updated": "string"
}
6.2. Health Check - /info/health (GET)

Returns whether the API is running properly.

Response:

{
  "status": "string",
  "success": "boolean"
}

