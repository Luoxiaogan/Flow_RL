# Workflow ID: hotpotqa_167_0
# Benchmark: hotpotqa
# Data Indices: [2454, 1070, 628, 2540, 2983]

<operator id="0">
    <instruction>Identify the key entities and relationships in the problem context to determine the correct answer.</instruction>
    <input>problem</input>
    <output>entity_relations</output>
  </operator>
  <operator id="1">
    <instruction>Extract candidate answers from the context based on the identified entities and relationships.</instruction>
    <input>entity_relations</input>
    <output>candidates</output>
  </operator>
  <operator id="2">
    <instruction>Evaluate each candidate against the question's requirements to determine the most accurate match.</instruction>
    <input>candidates</input>
    <output>evaluated_candidates</output>
  </operator>
  <operator id="3">
    <instruction>Filter out incorrect or irrelevant candidates based on logical consistency and contextual relevance.</instruction>
    <input>evaluated_candidates</input>
    <output>filtered_candidates</output>
  </operator>
  <operator id="4">
    <instruction>Verify the final candidate by cross-referencing with known facts or authoritative sources in the context.</instruction>
    <input>filtered_candidates</input>
    <output>verified_answer</output>
  </operator>
  <operator id="5">
    <instruction>Ensure the output is a single, unambiguous answer that directly addresses the question.</instruction>
    <input>verified_answer</input>
    <output>final_answer</output>
  </operator>