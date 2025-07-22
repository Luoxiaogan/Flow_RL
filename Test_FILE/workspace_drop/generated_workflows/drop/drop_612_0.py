# Workflow ID: drop_612_0
# Benchmark: drop
# Data Indices: [243, 3782, 1582, 3477]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key numerical data relevant to the question in the passage.</instruction>
    <input>1</input>
  </node>
  <node id="3" type="agent">
    <instruction>Compare the percentages or values provided for the two groups mentioned in the question.</instruction>
    <input>2</input>
  </node>
  <node id="4" type="agent">
    <instruction>Determine which group has the smaller percentage based on the comparison.</instruction>
    <input>3</input>
  </node>
  <node id="5" type="output">
    <input>4</input>
  </node>