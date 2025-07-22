# Workflow ID: drop_417_0
# Benchmark: drop
# Data Indices: [2213, 3073, 610, 3840, 775]

<operator id="0">
    <instruction>Extract all scoring plays from the passage, noting the player, type of score, and yardage.</instruction>
    <input>problem</input>
    <output>scoring_plays</output>
  </operator>
  <operator id="1">
    <instruction>Filter for touchdowns with a distance of at least 20 yards from the extracted scoring plays.</instruction>
    <input>scoring_plays</input>
    <output>long_touchdowns</output>
  </operator>
  <operator id="2">
    <instruction>Identify the players who scored these long touchdowns.</instruction>
    <input>long_touchdowns</input>
    <output>players_with_long_td</output>
  </operator>
  <operator id="3">
    <instruction>Return the list of players who scored touchdowns of at least 20 yards.</instruction>
    <input>players_with_long_td</input>
    <output>final_answer</output>
  </operator>