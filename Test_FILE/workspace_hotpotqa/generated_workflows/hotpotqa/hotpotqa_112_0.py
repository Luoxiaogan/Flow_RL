# Workflow ID: hotpotqa_112_0
# Benchmark: hotpotqa
# Data Indices: [3515, 1128, 396, 3282]

<operator id="0" type="agent">
    <instruction>Identify the key entities and relationships in the context to determine the correct answer.</instruction>
    <input>problem</input>
    <output>entity_list</output>
  </operator>
  <operator id="1" type="agent">
    <instruction>Extract relevant details from the entity list that directly address the question.</instruction>
    <input>entity_list</input>
    <output>relevant_info</output>
  </operator>
  <operator id="2" type="agent">
    <instruction>Verify the extracted information against known facts or timelines to ensure accuracy.</instruction>
    <input>relevant_info</input>
    <output>verified_answer</output>
  </operator>
  <operator id="3" type="agent">
    <instruction>Check for any conflicting data or missing links that might affect the result.</instruction>
    <input>verified_answer</input>
    <output>final_check</output>
  </operator>
  <operator id="4" type="agent">
    <instruction>Generate a concise and accurate response based on the final verification.</instruction>
    <input>final_check</input>
    <output>answer</output>
  </operator>
  <edge from="0" to="1" />
  <edge from="1" to="2" />
  <edge from="2" to="3" />
  <edge from="3" to="4" />