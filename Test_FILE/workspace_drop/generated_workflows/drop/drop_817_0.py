# Workflow ID: drop_817_0
# Benchmark: drop
# Data Indices: [3031, 1713, 700, 490, 1172]

<node id="1" type="input">
    <prompt>Understand the problem statement and identify key numerical or temporal data.</prompt>
  </node>
  <node id="2" type="process">
    <prompt>Extract relevant values from the passage that relate to the question.</prompt>
  </node>
  <node id="3" type="process">
    <prompt>Perform necessary calculations or comparisons based on extracted data.</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Formulate the final answer clearly and concisely.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>