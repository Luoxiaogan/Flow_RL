# Workflow ID: drop_819_0
# Benchmark: drop
# Data Indices: [1211, 1598, 3052, 597]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key information in the passage related to the question. Break down the passage step by step to locate the relevant details.</instruction>
    <input>1</input>
  </node>
  <node id="3" type="agent">
    <instruction>Extract numerical or categorical data that directly answers the question. Focus only on the values or facts that are explicitly mentioned.</instruction>
    <input>2</input>
  </node>
  <node id="4" type="agent">
    <instruction>Compare or analyze the extracted data logically to determine the correct answer based on the question's requirement.</instruction>
    <input>3</input>
  </node>
  <node id="5" type="output">
    <instruction>Return the final answer derived from the analysis. Ensure it is concise and directly addresses the original question.</instruction>
    <input>4</input>
  </node>