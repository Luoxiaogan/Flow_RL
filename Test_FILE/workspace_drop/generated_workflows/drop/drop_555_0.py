# Workflow ID: drop_555_0
# Benchmark: drop
# Data Indices: [2556, 2389, 1708, 3855]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
    <input>1</input>
    <output>3</output>
  </node>
  <node id="3" type="agent">
    <instruction>Identify the specific value or values that answer the question, considering all provided numbers and context.</instruction>
    <input>2</input>
    <output>4</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify that the identified value matches the exact requirement of the question (e.g., shortest, longest, percentage, etc.).</instruction>
    <input>3</input>
    <output>5</output>
  </node>
  <node id="5" type="output">
    <data>4</data>
  </node>