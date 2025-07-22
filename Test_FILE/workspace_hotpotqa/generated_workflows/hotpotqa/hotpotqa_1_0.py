# Workflow ID: hotpotqa_1_0
# Benchmark: hotpotqa
# Data Indices: [310, 3227, 2402, 2185]

<agent id="1" type="extract">
    <instruction>Identify the key entities and relationships in the context that directly answer the question.</instruction>
  </agent>
  <agent id="2" type="filter">
    <instruction>From the extracted entities, filter those relevant to the specific question being asked.</instruction>
  </agent>
  <agent id="3" type="reason">
    <instruction>Use logical reasoning to connect filtered entities and deduce the correct answer step by step.</instruction>
  </agent>
  <agent id="4" type="validate">
    <instruction>Verify the derived answer against the context to ensure accuracy and relevance.</instruction>
  </agent>
  <agent id="5" type="ensemble">
    <instruction>Combine outputs from all agents into a single coherent final answer.</instruction>
  </agent>
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="3" to="4"/>
  <connection from="4" to="5"/>