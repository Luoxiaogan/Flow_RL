# Workflow ID: hotpotqa_89_0
# Benchmark: hotpotqa
# Data Indices: [3517, 1116, 788, 825, 2159]

<start>
    <task>Extract key entities from the question</task>
    <next>Identify relevant context for each entity</next>
  </start>

  <node id="Identify relevant context for each entity">
    <task>Search for information about each entity in provided context</task>
    <next>Filter matches that directly answer the question</next>
  </node>

  <node id="Filter matches that directly answer the question">
    <task>Validate which context explicitly answers the question</task>
    <next>Generate final answer based on validated context</next>
  </node>

  <node id="Generate final answer based on validated context">
    <task>Construct a concise and accurate response</task>
    <next>End</next>
  </node>

  <end/>