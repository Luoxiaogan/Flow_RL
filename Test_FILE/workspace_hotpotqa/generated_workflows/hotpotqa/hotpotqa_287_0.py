# Workflow ID: hotpotqa_287_0
# Benchmark: hotpotqa
# Data Indices: [3251, 1202, 3724, 3053]

<agent id="1" type="query_expansion">
    <instruction>Break down the question into core components and identify key entities that need to be verified.</instruction>
  </agent>
  <agent id="2" type="context_analysis">
    <instruction>Extract relevant information from the provided context that directly answers the question. Focus only on what is necessary to resolve the query.</instruction>
  </agent>
  <agent id="3" type="entity_resolution">
    <instruction>Determine if the entities mentioned in the question (e.g., Carl Wayne, Ken) are both singers and actors by cross-referencing with the context.</instruction>
  </agent>
  <agent id="4" type="verification">
    <instruction>Validate each entity's dual role as singer and actor using evidence from the context. If either role is missing, flag accordingly.</instruction>
  </agent>
  <agent id="5" type="consolidation">
    <instruction>Combine findings from all agents to produce a final answer that precisely addresses whether both individuals meet both criteria.</instruction>
  </agent>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>