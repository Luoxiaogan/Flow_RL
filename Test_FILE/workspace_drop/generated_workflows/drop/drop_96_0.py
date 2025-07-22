# Workflow ID: drop_96_0
# Benchmark: drop
# Data Indices: [1472, 877, 1567, 344]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
    <input>1</input>
    <output>2</output>
  </node>
  <node id="3" type="agent">
    <instruction>Identify the key values needed to answer the question step by step.</instruction>
    <input>2</input>
    <output>3</output>
  </node>
  <node id="4" type="agent">
    <instruction>Perform the required arithmetic or comparison operation based on extracted values.</instruction>
    <input>3</input>
    <output>4</output>
  </node>
  <node id="5" type="agent">
    <instruction>Verify that the calculation aligns with the question's requirement and context.</instruction>
    <input>4</input>
    <output>5</output>
  </node>
  <node id="6" type="output">
    <input>5</input>
  </node>