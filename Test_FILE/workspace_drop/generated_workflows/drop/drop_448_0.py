# Workflow ID: drop_448_0
# Benchmark: drop
# Data Indices: [222, 3066, 3924, 3634]

<node id="1" type="input">
    <prompt>Read the passage carefully and identify all instances where a player receives a pass for a touchdown.</prompt>
  </node>
  <node id="2" type="process">
    <prompt>Extract each passing touchdown from the passage, noting the receiver and the quarterback.</prompt>
  </node>
  <node id="3" type="filter">
    <prompt>Identify only the receiving touchdowns attributed to Keiland Williams.</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Count how many times Keiland Williams received a pass for a touchdown. Return this number as an integer.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>