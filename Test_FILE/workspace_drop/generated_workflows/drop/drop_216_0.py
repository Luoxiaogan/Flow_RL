# Workflow ID: drop_216_0
# Benchmark: drop
# Data Indices: [2585, 3087, 2501, 1036]

<start/>
  <node id="1" type="agent">
    <instruction>Identify the key event or statistic mentioned in the passage related to the question.</instruction>
    <input>problem</input>
    <output>event_or_statistic</output>
  </node>
  <node id="2" type="agent">
    <instruction>Extract the relevant player and yardage from the identified event or statistic.</instruction>
    <input>event_or_statistic</input>
    <output>player_and_yardage</output>
  </node>
  <node id="3" type="agent">
    <instruction>Determine if this is the longest instance of its kind in the game based on all similar events mentioned.</instruction>
    <input>player_and_yardage</input>
    <output>longest_instance</output>
  </node>
  <node id="4" type="agent">
    <instruction>Return the player who achieved the longest instance as the final answer.</instruction>
    <input>longest_instance</input>
    <output>final_answer</output>
  </node>
  <end/>
  <edge from="start" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="end"/>