# Workflow ID: drop_383_0
# Benchmark: drop
# Data Indices: [612, 2622, 2279, 2044]

<node id="1" type="input">
    <prompt>Understand the question and identify key data points needed to solve it.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant numerical values from the passage for comparison.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Compare the two values to determine which is larger.</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Return the group with the higher percentage as the answer.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>