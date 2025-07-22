# Workflow ID: drop_110_0
# Benchmark: drop
# Data Indices: [2541, 1000, 2707, 1896, 835]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage that answers the question.</instruction>
    <input>1</input>
  </node>
  <node id="3" type="agent">
    <instruction>Perform arithmetic operations if needed to derive the final answer based on extracted data.</instruction>
    <input>2</input>
  </node>
  <node id="4" type="output">
    <data>3</data>
    <input>3</input>
  </node>