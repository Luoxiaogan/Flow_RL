# Workflow ID: drop_748_0
# Benchmark: drop
# Data Indices: [509, 1758, 383, 2548]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
    <input>1</input>
  </node>
  <node id="3" type="agent">
    <instruction>Identify the specific metric or category being asked in the question.</instruction>
    <input>1</input>
  </node>
  <node id="4" type="agent">
    <instruction>Compare the extracted values to determine which is smaller or calculate the required quantity.</instruction>
    <input>2</input>
    <input>3</input>
  </node>
  <node id="5" type="agent">
    <instruction>Verify the final answer by cross-checking with the passage context.</instruction>
    <input>4</input>
  </node>
  <node id="6" type="output">
    <input>5</input>
  </node>