# Workflow ID: drop_506_0
# Benchmark: drop
# Data Indices: [262, 2825, 3245, 3774]

<node id="1" type="input">
    <prompt>Understand the question and identify key elements needed to solve it.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from the passage that directly answers the question. Focus on numerical values, names, or events tied to the query.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Compare or calculate based on the extracted data to determine the exact answer required by the question.</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Provide the final answer clearly and concisely, ensuring it matches the format of the question.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>