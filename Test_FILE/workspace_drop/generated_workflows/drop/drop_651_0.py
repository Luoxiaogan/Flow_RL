# Workflow ID: drop_651_0
# Benchmark: drop
# Data Indices: [788, 3879, 2160, 1891]

<node id="1" type="input">
    <prompt>Understand the question and extract key information.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify the relevant data in the passage that answers the question. Think step by step.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Compare the values or entities mentioned in the passage to determine the answer.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify that the comparison aligns with the question asked.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Provide the final answer based on the verified comparison.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>