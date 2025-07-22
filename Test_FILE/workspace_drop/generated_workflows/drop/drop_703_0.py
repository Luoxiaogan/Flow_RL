# Workflow ID: drop_703_0
# Benchmark: drop
# Data Indices: [3009, 2119, 2578, 1563, 69]

<node id="input" type="input"/>
  <node id="agent1" type="agent">
    <prompt>Think step by step to extract the key entities and relationships from the input. Identify what is being asked and what information in the passage directly answers the question.</prompt>
  </node>
  <node id="agent2" type="agent">
    <prompt>Based on the extracted entities, determine which specific data point or statement in the passage directly answers the question. If multiple pieces of information exist, prioritize the most relevant one.</prompt>
  </node>
  <node id="agent3" type="agent">
    <prompt>Verify that the answer derived from the passage is unambiguous and directly responsive to the question. If not, re-evaluate using the previous steps.</prompt>
  </node>
  <node id="output" type="output"/>
  <edge from="input" to="agent1"/>
  <edge from="agent1" to="agent2"/>
  <edge from="agent2" to="agent3"/>
  <edge from="agent3" to="output"/>