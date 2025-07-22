# Workflow ID: drop_278_0
# Benchmark: drop
# Data Indices: [3234, 1488, 225, 1140]

<node id="1" type="input">
    <param>problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question. Identify all values mentioned that could be used in calculations.</instruction>
    <input>1</input>
    <output>2</output>
  </node>
  <node id="3" type="agent">
    <instruction>Perform the necessary arithmetic or percentage calculation based on the extracted values. Ensure precision and correct interpretation of the question's intent.</instruction>
    <input>2</input>
    <output>3</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the result by cross-checking with the original passage for consistency and correctness of the applied logic.</instruction>
    <input>3</input>
    <output>4</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
  </node>