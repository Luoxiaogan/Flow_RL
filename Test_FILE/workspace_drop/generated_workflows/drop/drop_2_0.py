# Workflow ID: drop_2_0
# Benchmark: drop
# Data Indices: [1726, 215, 2349, 3998]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  <node id="2" type="agent">
    <description>Identify key players and scores mentioned in the passage</description>
    <instruction>Read the passage carefully. Extract all touchdown-scoring plays, including the player who scored, the yardage, and the quarter in which it occurred.</instruction>
  </node>
  <node id="3" type="agent">
    <description>Determine the last scoring play in the game</description>
    <instruction>From the extracted plays, identify the final touchdown scored based on the chronological order of quarters and plays within each quarter.</instruction>
  </node>
  <node id="4" type="agent">
    <description>Verify the scorer of the last touchdown</description>
    <instruction>Confirm that the identified last touchdown was indeed a touchdown (not a field goal or other score) and note the player who scored it.</instruction>
  </node>
  <node id="5" type="output">
    <description>Return the name of the player who scored the last touchdown</description>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>