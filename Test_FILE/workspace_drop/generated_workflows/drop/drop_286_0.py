# Workflow ID: drop_286_0
# Benchmark: drop
# Data Indices: [1555, 441, 1826, 566, 943]

<node id="1" type="input">
    <prompt>Understand the question and identify key information needed to solve it.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant data from the passage that directly answers the question. Focus on specific numbers, events, or counts mentioned.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Perform necessary calculations or logical deductions using the extracted data to derive the final answer.</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Provide the final answer clearly and concisely based on the previous steps.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>