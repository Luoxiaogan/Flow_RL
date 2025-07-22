# Workflow ID: drop_874_0
# Benchmark: drop
# Data Indices: [1588, 2907, 3313, 2813]

<node id="1" type="input">
    <prompt>Understand the question and identify the key information needed to solve it.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant details from the passage that directly relate to the question. Focus only on the specific data required.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Perform necessary calculations or comparisons using the extracted data to derive the answer.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify the result by cross-checking with the passage to ensure accuracy and completeness.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on the verified result.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>