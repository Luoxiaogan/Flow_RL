# Workflow ID: drop_36_0
# Benchmark: drop
# Data Indices: [3957, 1227, 1356, 3805, 1863]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to field goals and their distances.</instruction>
    <input>1</input>
  </node>
  <node id="3" type="agent">
    <instruction>Filter field goals that were kicked between 25 and 50 yards inclusive.</instruction>
    <input>2</input>
  </node>
  <node id="4" type="agent">
    <instruction>Count the number of filtered field goals.</instruction>
    <input>3</input>
  </node>
  <node id="5" type="output">
    <input>4</input>
  </node>