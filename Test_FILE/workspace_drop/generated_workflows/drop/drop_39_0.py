# Workflow ID: drop_39_0
# Benchmark: drop
# Data Indices: [2240, 33, 2166, 1245]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the relevant numerical data in the passage that pertains to the question.</instruction>
    <input>1</input>
  </node>
  <node id="3" type="agent">
    <instruction>Compare the values to determine which group is smaller based on the provided percentages.</instruction>
    <input>2</input>
  </node>
  <node id="4" type="output">
    <instruction>Return the age group with the smaller percentage.</instruction>
    <input>3</input>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>