# Workflow ID: drop_858_0
# Benchmark: drop
# Data Indices: [721, 1990, 555, 3447]

<node id="1" type="input">
    <prompt>Extract relevant numerical data from the passage related to the question.</prompt>
  </node>
  <node id="2" type="operator">
    <prompt>Identify and isolate the specific values needed to answer the question. For example, in Problem 1, find Andersen's and Tynes' field goal distances.</prompt>
  </node>
  <node id="3" type="operator">
    <prompt>Perform the required arithmetic operation: subtract the smaller value from the larger one to find the difference.</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Return the computed difference as the final answer.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>