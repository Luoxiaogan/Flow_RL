# Workflow ID: drop_130_0
# Benchmark: drop
# Data Indices: [3046, 3573, 686, 1969, 2903]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key elements in the passage relevant to the question. Break down the passage into chronological events or score updates.</instruction>
    <input>1</input>
    <output>parsed_events</output>
  </node>
  <node id="3" type="agent">
    <instruction>Extract all scoring plays and their distances from the passage. Focus only on field goals over 30 yards.</instruction>
    <input>2</input>
    <output>field_goals_over_30</output>
  </node>
  <node id="4" type="agent">
    <instruction>Determine which player scored the first field goal over 30 yards by comparing timestamps of each such field goal.</instruction>
    <input>3</input>
    <output>first_player_over_30</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
    <output>final_answer</output>
  </node>