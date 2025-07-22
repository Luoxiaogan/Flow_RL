# Workflow ID: drop_730_0
# Benchmark: drop
# Data Indices: [3320, 3726, 2204, 3122, 2792]

<node id="1" type="input">
    <param>problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage that answers the question. Identify key values and their context.</instruction>
    <input>1</input>
    <output>2</output>
  </node>
  <node id="3" type="agent">
    <instruction>Perform arithmetic or logical operations using the extracted values to compute the answer. Ensure units and comparisons are correct.</instruction>
    <input>2</input>
    <output>3</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the computed result by cross-checking with original passage details. Confirm no misinterpretation of values occurred.</instruction>
    <input>3</input>
    <output>4</output>
  </node>
  <node id="5" type="agent">
    <instruction>Format the final answer clearly, ensuring it directly responds to the question without extra text.</instruction>
    <input>4</input>
    <output>5</output>
  </node>
  <node id="6" type="output">
    <param>answer</param>
    <input>5</input>
  </node>