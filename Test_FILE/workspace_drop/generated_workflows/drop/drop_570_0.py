# Workflow ID: drop_570_0
# Benchmark: drop
# Data Indices: [2097, 1527, 2673, 1453]

<node id="1">
    <task>Extract all scoring plays from the passage</task>
    <input>problem</input>
    <output>list_of_plays</output>
  </node>
  <node id="2">
    <task>Identify touchdown receptions and their yardages</task>
    <input>list_of_plays</input>
    <output>touchdown_receptions</output>
  </node>
  <node id="3">
    <task>Find the longest touchdown reception</task>
    <input>touchdown_receptions</input>
    <output>longest_touchdown_reception</output>
  </node>
  <node id="4">
    <task>Extract player name associated with the longest touchdown reception</task>
    <input>longest_touchdown_reception</input>
    <output>player_name</output>
  </node>
  <node id="5">
    <task>Return the player who scored the longest touchdown reception</task>
    <input>player_name</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>