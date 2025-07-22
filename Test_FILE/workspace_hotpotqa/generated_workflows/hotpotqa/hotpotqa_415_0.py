# Workflow ID: hotpotqa_415_0
# Benchmark: hotpotqa
# Data Indices: [2506, 3670, 3800, 352, 2274]

<operator id="0" type="agent">
    <instruction>Think step by step to identify the core question and relevant context.</instruction>
    <input>problem</input>
    <output>core_question, relevant_context</output>
  </operator>
  <operator id="1" type="agent">
    <instruction>Extract key entities and relationships from the relevant context that directly address the core question.</instruction>
    <input>relevant_context</input>
    <output>key_entities, relationships</output>
  </operator>
  <operator id="2" type="agent">
    <instruction>Validate each entity and relationship against known facts or logical consistency.</instruction>
    <input>key_entities, relationships</input>
    <output>validated_entities, valid_relationships</output>
  </operator>
  <operator id="3" type="agent">
    <instruction>Construct a minimal answer based on validated entities and relationships.</instruction>
    <input>validated_entities, valid_relationships</input>
    <output>answer</output>
  </operator>
  <operator id="4" type="agent">
    <instruction>Double-check that the answer is fully supported by the original context and logically sound.</instruction>
    <input>answer, problem</input>
    <output>final_answer</output>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>