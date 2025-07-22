# Workflow ID: drop_211_0
# Benchmark: drop
# Data Indices: [2375, 171, 2614, 437]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Extract the relevant numerical values from the passage that correspond to the question asked. Identify the key entities and their associated numbers.</instruction>
    <input>1</input>
    <output>2</output>
  </node>
  <node id="3" type="agent">
    <instruction>Perform the required arithmetic operation (e.g., subtraction, comparison) using the extracted values to compute the final answer.</instruction>
    <input>2</input>
    <output>3</output>
  </node>
  <node id="4" type="output">
    <input>3</input>
    <parameter>answer</parameter>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>