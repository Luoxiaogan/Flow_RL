# Workflow ID: hotpotqa_100_0
# Benchmark: hotpotqa
# Data Indices: [816, 2924, 1073, 3320]

<operator id="0">
    <instruction>Identify the key entities and relationships in the problem statement.</instruction>
    <input>problem</input>
    <output>entity_list, relationship_graph</output>
  </operator>
  <operator id="1">
    <instruction>Extract relevant facts from the context that directly answer the question.</instruction>
    <input>context, entity_list</input>
    <output>relevant_facts</output>
  </operator>
  <operator id="2">
    <instruction>Validate each fact against the question to determine if it provides a direct answer.</instruction>
    <input>relevant_facts, question</input>
    <output>valid_answers</output>
  </operator>
  <operator id="3">
    <instruction>Aggregate all valid answers into a coherent final response.</instruction>
    <input>valid_answers</input>
    <output>final_answer</output>
  </operator>
  <operator id="4">
    <instruction>Ensure no extraneous information is included in the final answer; only return what was directly supported by the context.</instruction>
    <input>final_answer</input>
    <output>clean_final_answer</output>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>