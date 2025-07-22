# Workflow ID: drop_336_0
# Benchmark: drop
# Data Indices: [750, 1890, 711, 2244]

<node id="start" type="input"/>
  <node id="agent1" type="agent">
    <instruction>Identify all touchdown passes in the passage and record their yardages.</instruction>
  </node>
  <node id="agent2" type="agent">
    <instruction>From the list of touchdown pass yardages, determine the two smallest values.</instruction>
  </node>
  <node id="agent3" type="agent">
    <instruction>Verify that these two values are indeed the shortest touchdown passes by cross-checking with the original text.</instruction>
  </node>
  <node id="output" type="output"/>
  <edge from="start" to="agent1"/>
  <edge from="agent1" to="agent2"/>
  <edge from="agent2" to="agent3"/>
  <edge from="agent3" to="output"/>