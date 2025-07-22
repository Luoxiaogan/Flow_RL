# Workflow ID: drop_597_0
# Benchmark: drop
# Data Indices: [1963, 2846, 3328, 2555]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant data from the passage for calculating percentages.</instruction>
    <input>1</input>
    <output>2</output>
  </node>
  <node id="3" type="agent">
    <instruction>Calculate the percentage of non-White population by subtracting White percentage from 100.</instruction>
    <input>2</input>
    <output>3</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the calculation to ensure accuracy and consistency with given data.</instruction>
    <input>3</input>
    <output>4</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
  </node>