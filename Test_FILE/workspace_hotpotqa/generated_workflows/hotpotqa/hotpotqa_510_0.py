# Workflow ID: hotpotqa_510_0
# Benchmark: hotpotqa
# Data Indices: [3056, 320, 3379, 3933]

<operator id="0">
    <instruction>Understand the core question and identify key entities mentioned.</instruction>
    <input>problem</input>
    <output>key_entities</output>
  </operator>
  <operator id="1">
    <instruction>Extract relevant context that links the key entities to the answer.</instruction>
    <input>key_entities, context</input>
    <output>linked_context</output>
  </operator>
  <operator id="2">
    <instruction>Validate each piece of linked context for accuracy and relevance to the question.</instruction>
    <input>linked_context</input>
    <output>validated_info</output>
  </operator>
  <operator id="3">
    <instruction>Construct a logical path from validated information to derive the final answer.</instruction>
    <input>validated_info</input>
    <output>answer</output>
  </operator>
  <operator id="4">
    <instruction>Double-check the derived answer against all available context to ensure consistency.</instruction>
    <input>answer, context</input>
    <output>final_answer</output>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>