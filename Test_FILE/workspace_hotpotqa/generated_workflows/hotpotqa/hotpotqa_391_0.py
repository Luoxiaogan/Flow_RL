# Workflow ID: hotpotqa_391_0
# Benchmark: hotpotqa
# Data Indices: [1641, 2769, 3291, 1785]

<node id="1">
    <task>Identify the key entities in the question</task>
    <input>question</input>
    <output>entities</output>
  </node>
  <node id="2">
    <task>Retrieve relevant context for each entity</task>
    <input>entities, context</input>
    <output>filtered_context</output>
  </node>
  <node id="3">
    <task>Extract specific information from filtered context</task>
    <input>filtered_context</input>
    <output>candidate_answers</output>
  </node>
  <node id="4">
    <task>Validate candidate answers against question semantics</task>
    <input>candidate_answers, question</input>
    <output>valid_answers</output>
  </node>
  <node id="5">
    <task>Return the final answer(s)</task>
    <input>valid_answers</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>