# Workflow ID: hotpotqa_20_0
# Benchmark: hotpotqa
# Data Indices: [1424, 505, 1389, 3153, 1977]

<operator id="1">
    <instruction>Identify the key entities in the question and context that relate to the answer.</instruction>
    <input>problem</input>
    <output>entity_candidates</output>
  </operator>
  <operator id="2">
    <instruction>Filter candidates to find the one directly answering the question by matching roles, relationships, or attributes.</instruction>
    <input>entity_candidates</input>
    <output>filtered_entity</output>
  </operator>
  <operator id="3">
    <instruction>Extract the relevant attribute (e.g., birth year) from the filtered entity.</instruction>
    <input>filtered_entity</input>
    <output>birth_year</output>
  </operator>
  <operator id="4">
    <instruction>Verify that the extracted birth year matches the context of the film and co-star relationship described.</instruction>
    <input>birth_year</input>
    <output>verification_result</output>
  </operator>
  <operator id="5">
    <instruction>Return the verified birth year as the final answer.</instruction>
    <input>verification_result</input>
    <output>final_answer</output>
  </operator>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>