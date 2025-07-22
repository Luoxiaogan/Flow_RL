# Workflow ID: drop_394_0
# Benchmark: drop
# Data Indices: [2444, 3880, 952, 1591, 1328]

<node id="1" type="input">
    <param>problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Extract all field goal distances from the passage. List them as integers.</instruction>
    <input>1</input>
    <output>field_goals</output>
  </node>
  <node id="3" type="agent">
    <instruction>Find the maximum and minimum values from the list of field goals. Return both as a tuple (max, min).</instruction>
    <input>2</input>
    <output>min_max</output>
  </node>
  <node id="4" type="agent">
    <instruction>Calculate the difference between the maximum and minimum field goal distances. Return this integer value.</instruction>
    <input>3</input>
    <output>difference</output>
  </node>
  <node id="5" type="output">
    <param>difference</param>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>