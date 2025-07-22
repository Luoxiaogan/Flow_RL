# Workflow ID: drop_877_0
# Benchmark: drop
# Data Indices: [824, 2423, 435, 815]

<node id="1" type="input">
    <prompt>Extract all field goal distances mentioned in the passage.</prompt>
  </node>
  <node id="2" type="process">
    <prompt>Convert the extracted field goal distances into a list of integers.</prompt>
  </node>
  <node id="3" type="process">
    <prompt>Sort the list of field goal distances in ascending order.</prompt>
  </node>
  <node id="4" type="process">
    <prompt>Identify the third element in the sorted list (index 2).</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the third shortest field goal distance.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>