# Workflow ID: drop_582_0
# Benchmark: drop
# Data Indices: [840, 668, 1161, 3818, 2954]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
    <input>1</input>
  </node>
  <node id="3" type="agent">
    <instruction>Perform necessary calculations using the extracted data to answer the question step by step.</instruction>
    <input>2</input>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the calculation logic and ensure no steps are missed or misinterpreted.</instruction>
    <input>3</input>
  </node>
  <node id="5" type="output">
    <instruction>Return the final answer based on verified calculation.</instruction>
    <input>4</input>
  </node>