# Workflow ID: drop_429_0
# Benchmark: drop
# Data Indices: [3115, 2580, 849, 1543, 514]

<node id="1" type="input">
    <prompt>Understand the question and identify key elements needed to solve it.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant data from the passage related to the question. Focus only on the specific information required.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Compare or calculate based on the extracted data to answer the question directly.</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Return the final answer clearly and concisely.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>