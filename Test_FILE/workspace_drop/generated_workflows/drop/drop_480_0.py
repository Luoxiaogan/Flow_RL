# Workflow ID: drop_480_0
# Benchmark: drop
# Data Indices: [1306, 2002, 1879, 3415, 525]

<node id="1" type="input">
    <prompt>Understand the question and identify key information needed to solve it.</prompt>
  </node>
  <node id="2" type="process">
    <prompt>Extract relevant data from the passage that directly answers the question.</prompt>
  </node>
  <node id="3" type="process">
    <prompt>Apply logical reasoning or mathematical operations if required (e.g., summing scores, comparing averages).</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Provide the final answer based on processed information.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>