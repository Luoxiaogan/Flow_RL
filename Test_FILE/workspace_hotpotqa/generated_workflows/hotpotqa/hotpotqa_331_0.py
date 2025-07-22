# Workflow ID: hotpotqa_331_0
# Benchmark: hotpotqa
# Data Indices: [3253, 2737, 3308, 2318, 3623]

<node id="1">
    <task>Identify the key entity in the question</task>
    <input>problem</input>
    <output>entity</output>
  </node>
  <node id="2">
    <task>Extract relevant context related to the entity</task>
    <input>entity, context</input>
    <output>relevant_context</output>
  </node>
  <node id="3">
    <task>Parse and filter context for direct answer clues</task>
    <input>relevant_context</input>
    <output>clues</output>
  </node>
  <node id="4">
    <task>Validate clues against known facts or definitions</task>
    <input>clues</input>
    <output>validated_answer</output>
  </node>
  <node id="5">
    <task>Format final answer clearly and concisely</task>
    <input>validated_answer</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>