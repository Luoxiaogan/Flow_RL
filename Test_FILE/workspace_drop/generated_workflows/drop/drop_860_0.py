# Workflow ID: drop_860_0
# Benchmark: drop
# Data Indices: [3136, 2787, 80, 3194, 3569]

<node id="1" type="input">
    <prompt>Read the passage carefully and identify the key information relevant to the question.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract the specific numerical value or fact that directly answers the question from the passage. Think step by step: locate the sentence containing the answer, then isolate the exact number or term.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Verify that the extracted value matches the question's requirements. If it does not, re-examine the passage for any alternative references or clarifications.</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Return the final answer as a concise, accurate response based on the verified information from node 3.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>