# Workflow ID: drop_1_0
# Benchmark: drop
# Data Indices: [1183, 2708, 768, 2235]

<node id="1" type="input">
    <prompt>Extract the relevant numerical data from the passage related to the question.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify all field goal distances mentioned in the passage. For each, determine if it belongs to the player in question or not.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Sum all field goal distances attributed to the specified kicker (e.g., Mike Nugent).</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Find the maximum field goal distance among those recorded for the kicker.</prompt>
  </node>
  <node id="5" type="agent">
    <prompt>Compare the total yards and longest field goal to ensure both values are correctly derived.</prompt>
  </node>
  <node id="6" type="output">
    <prompt>Return the total yards kicked for field goals and the longest field goal distance as a tuple.</prompt>
  </node>

  <!-- Edges -->
  <edge from="1" to="2"/>
  <edge from="1" to="3"/>
  <edge from="1" to="4"/>
  <edge from="2" to="5"/>
  <edge from="3" to="5"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>