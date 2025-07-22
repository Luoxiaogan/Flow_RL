# Workflow ID: drop_376_0
# Benchmark: drop
# Data Indices: [2058, 3036, 1886, 3106]

<node id="1" type="input">
    <prompt>Understand the task and identify key elements from the input.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information step by step from the passage to answer the question.</prompt>
    <dependencies>1</dependencies>
  </node>
  <node id="3" type="agent">
    <prompt>Verify that the extracted information directly addresses the question asked.</prompt>
    <dependencies>2</dependencies>
  </node>
  <node id="4" type="agent">
    <prompt>Ensure no irrelevant data is included in the final answer.</prompt>
    <dependencies>3</dependencies>
  </node>
  <node id="5" type="output">
    <prompt>Return the final, concise answer based on verified information.</prompt>
    <dependencies>4</dependencies>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>