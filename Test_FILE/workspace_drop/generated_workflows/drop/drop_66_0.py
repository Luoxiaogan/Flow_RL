# Workflow ID: drop_66_0
# Benchmark: drop
# Data Indices: [2254, 2758, 2799, 2280, 1659]

<node id="1" type="input">
    <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
  </node>
  <node id="2" type="process">
    <instruction>Identify the longest and shortest field goal distances from the extracted data.</instruction>
  </node>
  <node id="3" type="compute">
    <instruction>Calculate the difference between the longest and shortest field goals.</instruction>
  </node>
  <node id="4" type="output">
    <instruction>Return the calculated difference as the final answer.</instruction>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>