# Workflow ID: drop_311_0
# Benchmark: drop
# Data Indices: [1272, 1793, 1905, 933]

<node id="1">
    <instruction>Extract all scoring events from the passage, identifying teams, scores, and time of each event.</instruction>
    <output>list_of_scores</output>
  </node>
  <node id="2">
    <instruction>Calculate total points for each team by summing their respective scores from list_of_scores.</instruction>
    <input>list_of_scores</input>
    <output>team_points</output>
  </node>
  <node id="3">
    <instruction>Determine the winning margin by subtracting the lower score from the higher score in team_points.</instruction>
    <input>team_points</input>
    <output>winning_margin</output>
  </node>
  <node id="4">
    <instruction>Return the winning margin as the final answer.</instruction>
    <input>winning_margin</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>