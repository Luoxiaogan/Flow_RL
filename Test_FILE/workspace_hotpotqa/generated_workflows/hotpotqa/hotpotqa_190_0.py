# Workflow ID: hotpotqa_190_0
# Benchmark: hotpotqa
# Data Indices: [2289, 3072, 3509, 2476]

<operator id="0">
    <instruction>Identify the key entities and relationships in the problem statement.</instruction>
    <input>problem</input>
    <output>entity_relationships</output>
  </operator>
  <operator id="1">
    <instruction>Extract relevant contextual clues that directly answer the question.</instruction>
    <input>entity_relationships</input>
    <output>clues</output>
  </operator>
  <operator id="2">
    <instruction>Validate each clue against known facts from the context to ensure accuracy.</instruction>
    <input>clues</input>
    <output>validated_clues</output>
  </operator>
  <operator id="3">
    <instruction>Construct a logical chain of reasoning using validated clues to derive the answer.</instruction>
    <input>validated_clues</input>
    <output>reasoning_chain</output>
  </operator>
  <operator id="4">
    <instruction>Generate the final answer based on the reasoning chain.</instruction>
    <input>reasoning_chain</input>
    <output>final_answer</output>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>