# Workflow ID: drop_504_0
# Benchmark: drop
# Data Indices: [3241, 1355, 2904, 751]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the relevant numerical data in the passage related to the question.</instruction>
    <input>1</input>
  </node>
  <node id="3" type="agent">
    <instruction>Perform the necessary calculation based on the identified data to answer the question step by step.</instruction>
    <input>2</input>
  </node>
  <node id="4" type="output">
    <instruction>Return the final computed result as the answer.</instruction>
    <input>3</input>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>