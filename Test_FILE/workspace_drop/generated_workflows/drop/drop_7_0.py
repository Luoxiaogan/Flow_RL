# Workflow ID: drop_7_0
# Benchmark: drop
# Data Indices: [2020, 2304, 2573, 2662, 2561]

<node id="1" type="input">
    <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
  </node>
  <node id="2" type="process">
    <instruction>Identify the specific value that answers the question based on the extracted data.</instruction>
  </node>
  <node id="3" type="validate">
    <instruction>Verify that the extracted value directly addresses the question without ambiguity.</instruction>
  </node>
  <node id="4" type="output">
    <instruction>Return the validated answer as a concise numeric or textual response.</instruction>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>