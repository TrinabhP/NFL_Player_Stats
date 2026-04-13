# User Stories and Exceptions for NFL_PLayer_Stats

## 12 User Stories

1. As a scout, I want to add a new player's combine stats (40-yd dash, bench press, broad jump) so that their data is available for analysis.

2. As a fan, I want to look up a player by name and see their combine results so that I can learn more about their pre-draft profile.

3. As a general manager, I want to search for players with similar combine profiles to a specific NFL star so that I can identify comparable prospects.

4. As a player, I want to see players comparable to me and see how they succeed, so I can understand what I need to do.

5. As a team administrator, I want to be able to easily add a bulk amount of players stats to save time.

6. As a fan, I want to be able to see a rating of each player based on their physical attributes and their success in the NFL.

7. As a coach, I want to update a player’s stats if they were recorded incorrectly or for a new player, so that the data remains accurate and up to date

8. As a data analyst, I want to retrieve aggregated statistics (e.g., average 40-yard dash by position), so that I can identify trends across player groups.

9. As a developer, I want to retrieve player data through a public API endpoint, so that I can build applications and visualizations using the data.

10. As a sports journalist, I want to filter the database by college or university, so I can write stories about which program produces the best combine performers.

11. As an NFL prospect, I want to see how my combine numbers compare to the average for my position in the recent draft class, so that I have a good benchmark for my practice.

12. As a sports bettor, I want to see who has a good performance during the combine so I can make more informed bets on incoming NFL rookies during the pre-season.


## 12 Exceptions

1. Missing required fields
If a required field (such as player name or position) is omitted from a create request, the API returns a 400 Bad Request listing all missing fields.

2. Player not found
If a request is made for a player who does not exist in the database, the API returns a 404 Not Found error with a descriptive message.

3. Invalid position value
If a player is submitted with a position not in the allowed set (e.g., "small forward"), the API returns a 400 Bad Request with the list of valid positions.

4. Empty search results
If a filter query (e.g., by draft year) matches no players, the API returns a 200 OK with an empty list and a message indicating no results were found.

5. Incorrect input type
If an input like yards is put in as a float instead of an int the API returns a 400 Bad Request, incorrect input type error.

6. Duplicate player entry
If a user attempts to add a player that already exists (same name and draft year), the API returns a 409 Conflict error and prevents duplicate entries.

7. Invalid numeric range
If a stat such as 40-yard dash time or bench press reps is outside a realistic range, the API returns a 400 Bad Request with a message indicating valid value ranges.

8. Bulk upload failure
If a bulk upload contains invalid records, the API will reject the request and return a list of errors for each invalid entry so the user can correct them.

9. Developer exceeds rate limit
If the developer sends too many requests within a given time window the API will return an error indicating that too many requests were made with a message telling the developer to wait before making another request.

10. College name is not found
If the journalist searches for a college or university that does not exist in the database, the system will return an error message saying no results were found. This could come up when school names have alternate names (“California Polytechnic State University” or “Cal Poly”)

11. Not enough data on specific position
If there is little/no combine data recorded for the prospect’s position group in the database, the system will return a 404 or Not Found error when they attempt to search for the data.

12. Player’s combine results are incomplete
If a prospect only completed some drills, the system will still display their available metrics but will give an incomplete profile of the athlete.

 