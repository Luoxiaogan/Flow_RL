# Workflow ID: drop_127_0
# Benchmark: drop
# Data Indices: [276, 2761, 2901, 787]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="process">
    <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
  </node>
  <node id="3" type="process">
    <instruction>Perform necessary arithmetic operations (e.g., subtraction, percentage calculation).</instruction>
  </node>
  <node id="4" type="validate">
    <instruction>Verify that the computed result matches the expected logic of the question.</instruction>
  </node>
  <node id="5" type="output">
    <instruction>Return the final answer as a percentage or numeric value.</instruction>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>