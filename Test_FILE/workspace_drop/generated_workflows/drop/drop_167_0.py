# Workflow ID: drop_167_0
# Benchmark: drop
# Data Indices: [385, 2498, 1182, 161]

<node id="1" type="input">
    <prompt>Understand the question and identify key data points.</prompt>
  </node>
  <node id="2" type="process">
    <prompt>Extract relevant numerical values from the passage related to the query.</prompt>
  </node>
  <node id="3" type="process">
    <prompt>Apply mathematical operations (e.g., subtraction, addition) based on the question.</prompt>
  </node>
  <node id="4" type="validate">
    <prompt>Verify that all required data has been used and calculations are correct.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Provide the final answer in a clear format.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>