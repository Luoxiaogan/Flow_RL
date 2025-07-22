# Workflow ID: drop_270_0
# Benchmark: drop
# Data Indices: [277, 1405, 3966, 2495]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract the relevant numerical values from the passage for comparison.</instruction>
    <input>1</input>
    <output>2</output>
  </node>
  <node id="3" type="agent">
    <instruction>Calculate the difference between the two percentages mentioned in the problem.</instruction>
    <input>2</input>
    <output>3</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify that the calculation is correct and matches the question's requirement.</instruction>
    <input>3</input>
    <output>4</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
  </node>