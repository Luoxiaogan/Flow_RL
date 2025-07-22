# Workflow ID: drop_650_0
# Benchmark: drop
# Data Indices: [2822, 1074, 266, 1751]

<node id="1" type="input">
    <param name="problem" />
  </node>
  <node id="2" type="agent">
    <instruction>Extract all scoring plays from the passage, including touchdowns and field goals, along with their yardages.</instruction>
    <input>1</input>
    <output>plays_list</output>
  </node>
  <node id="3" type="agent">
    <instruction>Filter for plays that occurred in the first two quarters only.</instruction>
    <input>2</input>
    <output>first_two_quarters_plays</output>
  </node>
  <node id="4" type="agent">
    <instruction>Sum the yardages of all touchdowns and field goals from the filtered list.</instruction>
    <input>3</input>
    <output>total_yards</output>
  </node>
  <node id="5" type="agent">
    <instruction>Identify field goals between 30 and 39 yards inclusive.</instruction>
    <input>2</input>
    <output>field_goals_30_39</output>
  </node>
  <node id="6" type="agent">
    <instruction>Count how many field goals were made in the range of 30 to 39 yards.</instruction>
    <input>5</input>
    <output>count_field_goals_30_39</output>
  </node>
  <node id="7" type="agent">
    <instruction>Determine which team scored in the second half by checking if any scores occurred after the third quarter.</instruction>
    <input>2</input>
    <output>teams_with_second_half_scores</output>
  </node>
  <node id="8" type="agent">
    <instruction>Calculate the difference in yardage between Byron Leftwich's touchdown run and Peyton Manning's touchdown run.</instruction>
    <input>2</input>
    <output>yardage_difference</output>
  </node>
  <node id="9" type="output">
    <input>4</input>
    <input>6</input>
    <input>7</input>
    <input>8</input>
    <output>final_results</output>
  </node>