# Workflow ID: drop_432_0
# Benchmark: drop
# Data Indices: [758, 1088, 729, 3949, 3171]

<node id="1" type="input">
    <prompt>Understand the problem and extract key numerical data.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify all relevant values mentioned in the passage related to the question. Think step by step to avoid missing any critical number.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Perform necessary arithmetic operations (e.g., subtraction, addition) based on the extracted values to compute the answer.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify that the computed result matches the exact requirement of the question—e.g., "how many times", "how many more", etc.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final numerical answer as a single integer.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>