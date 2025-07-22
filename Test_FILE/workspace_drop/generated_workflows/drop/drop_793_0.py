# Workflow ID: drop_793_0
# Benchmark: drop
# Data Indices: [399, 1960, 76, 2815, 2841]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities or metrics needed to answer it.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from the passage related to the question. Focus on specific values, names, or events mentioned.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Compare or calculate based on the extracted data to determine the correct answer.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Validate the result by cross-checking with the passage for consistency and accuracy.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer clearly and concisely based on the validated result.</prompt>
  </node>

  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>