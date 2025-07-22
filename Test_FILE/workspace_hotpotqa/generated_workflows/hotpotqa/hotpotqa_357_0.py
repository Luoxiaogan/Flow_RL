# Workflow ID: hotpotqa_357_0
# Benchmark: hotpotqa
# Data Indices: [1831, 521, 1507, 1941]

<operator id="0" type="agent">
    <instruction>Identify the key elements in the question and determine which entity is being asked about.</instruction>
    <input>problem</input>
    <output>entity_query</output>
  </operator>
  <operator id="1" type="agent">
    <instruction>Scan the context for mentions of the entity and extract all relevant information related to it.</instruction>
    <input>entity_query, context</input>
    <output>candidate_info</output>
  </operator>
  <operator id="2" type="agent">
    <instruction>Filter out irrelevant details and isolate the specific fact that directly answers the question.</instruction>
    <input>candidate_info</input>
    <output>direct_answer</output>
  </operator>
  <operator id="3" type="agent">
    <instruction>Verify the extracted answer against the original question to ensure correctness and relevance.</instruction>
    <input>direct_answer, problem</input>
    <output>verified_answer</output>
  </operator>
  <operator id="4" type="agent">
    <instruction>Format the verified answer into a concise, clear response suitable for direct output.</instruction>
    <input>verified_answer</input>
    <output>final_output</output>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>