# Workflow ID: drop_678_0
# Benchmark: drop
# Data Indices: [3496, 2392, 478, 3587, 3903]

<node id="start" type="input"/>
  <node id="agent1" type="agent">
    <instruction>Think step by step to identify the key data points relevant to the question.</instruction>
  </node>
  <node id="agent2" type="agent">
    <instruction>Extract and process numerical values from the passage that directly answer the question.</instruction>
  </node>
  <node id="agent3" type="agent">
    <instruction>Apply mathematical operations or logical reasoning to derive the final answer.</instruction>
  </node>
  <node id="output" type="output"/>
  <edge from="start" to="agent1"/>
  <edge from="agent1" to="agent2"/>
  <edge from="agent2" to="agent3"/>
  <edge from="agent3" to="output"/>