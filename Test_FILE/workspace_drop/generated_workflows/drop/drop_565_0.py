# Workflow ID: drop_565_0
# Benchmark: drop
# Data Indices: [960, 3356, 3346, 3302, 3144]

<node id="1" type="input">
    <prompt>Extract relevant numerical data from the passage related to the question.</prompt>
  </node>
  <node id="2" type="operator">
    <prompt>Identify and isolate the specific values needed to answer the question based on the extracted data.</prompt>
  </node>
  <node id="3" type="operator">
    <prompt>Perform necessary arithmetic or logical operations to derive the final answer from the isolated values.</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Return the computed result as the answer to the question.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>