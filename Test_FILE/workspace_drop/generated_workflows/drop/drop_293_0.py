# Workflow ID: drop_293_0
# Benchmark: drop
# Data Indices: [1847, 3251, 867, 1670, 1545]

<node id="1" type="input">
    <prompt>Understand the question and identify required data from the passage.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant numerical or percentage data from the passage based on the question.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Perform necessary arithmetic operations (e.g., subtraction, percentages, time difference).</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Validate intermediate result to ensure correctness of calculation.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer as a single number or percentage based on the problem's requirement.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>