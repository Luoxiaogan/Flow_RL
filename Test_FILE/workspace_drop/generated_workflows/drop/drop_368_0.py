# Workflow ID: drop_368_0
# Benchmark: drop
# Data Indices: [3719, 938, 3991, 377]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant data from the passage that answers the question. Focus on specific events, players, and numerical values mentioned.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Perform necessary calculations or comparisons based on extracted data to derive the answer.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify the result by cross-checking with the passage to ensure accuracy.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on verified results.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>