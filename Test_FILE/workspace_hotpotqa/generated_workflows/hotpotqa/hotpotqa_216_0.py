# Workflow ID: hotpotqa_216_0
# Benchmark: hotpotqa
# Data Indices: [75, 1573, 1498, 2024, 363]

<operator id="0">
    <instruction>Identify the key entities and relationships in the problem. Focus on the main subject and its attributes or associated elements.</instruction>
    <input>problem</input>
    <output>entity_list</output>
  </operator>
  <operator id="1">
    <instruction>For each entity, determine which one directly answers the question. Filter out irrelevant details based on the question's focus.</instruction>
    <input>entity_list</input>
    <output>candidate_answer</output>
  </operator>
  <operator id="2">
    <instruction>Verify the candidate answer by cross-referencing it with the context provided. Ensure it matches both the question and the supporting facts.</instruction>
    <input>candidate_answer</input>
    <output>verified_answer</output>
  </operator>
  <operator id="3">
    <instruction>Check for any indirect clues in the context that might support or contradict the verified answer. If found, update the answer accordingly.</instruction>
    <input>verified_answer</input>
    <output>final_answer</output>
  </operator>
  <operator id="4">
    <instruction>Ensure the final answer is concise and directly addresses the question without extraneous information.</instruction>
    <input>final_answer</input>
    <output>clean_final_answer</output>
  </operator>