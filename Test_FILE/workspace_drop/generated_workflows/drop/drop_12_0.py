# Workflow ID: drop_12_0
# Benchmark: drop
# Data Indices: [870, 89, 3267, 129, 927]

<node id="1" type="input">
    <instruction>Receive problem input and extract key numerical data.</instruction>
  </node>
  <node id="2" type="process">
    <instruction>Identify the relevant ratio or percentage from the passage that answers the question.</instruction>
  </node>
  <node id="3" type="compute">
    <instruction>Perform arithmetic operations (e.g., subtraction, division) to derive the answer.</instruction>
  </node>
  <node id="4" type="validate">
    <instruction>Verify that the computed result matches the logical structure of the question.</instruction>
  </node>
  <node id="5" type="output">
    <instruction>Return the final answer in the required format (e.g., integer, percent).</instruction>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>