# Workflow ID: drop_213_0
# Benchmark: drop
# Data Indices: [96, 145, 913, 3509, 2430]

<node id="1" type="input">
    <prompt>Understand the question and identify key elements to extract from the passage.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant data points related to the question. Focus on specific values, names, or events mentioned in the passage that directly answer the question.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Compare or calculate based on the extracted values to determine the correct answer.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Validate the result by cross-checking with the passage to ensure accuracy.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer clearly and concisely.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>