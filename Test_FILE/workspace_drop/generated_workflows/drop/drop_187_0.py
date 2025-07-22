# Workflow ID: drop_187_0
# Benchmark: drop
# Data Indices: [3000, 2716, 709, 1909]

<node id="1" type="input">
    <param name="problem">self.problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Understand the question and identify the key numerical values or relationships required to solve it. Break down the problem step by step.</instruction>
    <input>1</input>
  </node>
  <node id="3" type="agent">
    <instruction>Extract relevant data from the passage that directly answers the question. Ensure no irrelevant information is included.</instruction>
    <input>2</input>
  </node>
  <node id="4" type="agent">
    <instruction>Perform necessary calculations or comparisons based on the extracted data. If multiple operations are needed, execute them in sequence.</instruction>
    <input>3</input>
  </node>
  <node id="5" type="agent">
    <instruction>Verify the correctness of your solution by rechecking the logic and numbers used. Ensure no arithmetic or interpretation errors occurred.</instruction>
    <input>4</input>
  </node>
  <node id="6" type="output">
    <input>5</input>
  </node>