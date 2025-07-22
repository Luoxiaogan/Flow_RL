# Workflow ID: hotpotqa_508_0
# Benchmark: hotpotqa
# Data Indices: [565, 3182, 438, 3522]

<node id="start" type="input"/>
  <node id="agent1" type="agent">
    <instruction>Think step by step to identify the key information needed to solve the problem.</instruction>
  </node>
  <node id="agent2" type="agent">
    <instruction>Extract relevant facts from the context that directly address the question.</instruction>
  </node>
  <node id="agent3" type="agent">
    <instruction>Verify if the extracted facts are sufficient to answer the question definitively.</instruction>
  </node>
  <node id="agent4" type="agent">
    <instruction>Construct a clear and concise answer based on verified facts.</instruction>
  </node>
  <node id="end" type="output"/>
  <edge from="start" to="agent1"/>
  <edge from="agent1" to="agent2"/>
  <edge from="agent2" to="agent3"/>
  <edge from="agent3" to="agent4"/>
  <edge from="agent4" to="end"/>