# Workflow ID: hotpotqa_532_0
# Benchmark: hotpotqa
# Data Indices: [1612, 946, 469, 3310]

<operator id="0">
    <instruction>Identify the key entities and relationships in the problem statement. Focus on the main subject, its attributes, and any associated facts.</instruction>
    <input>problem</input>
    <output>parsed_entities</output>
  </operator>
  <operator id="1">
    <instruction>Map each entity to its relevant context or category (e.g., person, location, event). Ensure no duplication or ambiguity in classification.</instruction>
    <input>parsed_entities</input>
    <output>classified_entities</output>
  </operator>
  <operator id="2">
    <instruction>Extract direct answers from the context by matching the question's query with the classified entities. Prioritize explicit statements over inferred ones.</instruction>
    <input>classified_entities</input>
    <output>direct_answers</output>
  </operator>
  <operator id="3">
    <instruction>Verify that all steps of reasoning are logically connected and that each operator’s output contributes uniquely to the final answer.</instruction>
    <input>direct_answers</input>
    <output>verified_answer</output>
  </operator>
  <operator id="4">
    <instruction>Ensure the final answer is concise, directly addresses the question, and aligns with the verified result from the previous step.</instruction>
    <input>verified_answer</input>
    <output>final_output</output>
  </operator>