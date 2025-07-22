# Workflow ID: hotpotqa_120_0
# Benchmark: hotpotqa
# Data Indices: [954, 2111, 787, 341, 953]

<operator id="1">
    <instruction>Identify the key entities and relationships in the input context to determine the correct answer.</instruction>
    <input>problem</input>
    <output>candidate_answers</output>
  </operator>
  <operator id="2">
    <instruction>Filter candidate answers based on direct relevance to the question, eliminating irrelevant or misleading options.</instruction>
    <input>candidate_answers</input>
    <output>filtered_answers</output>
  </operator>
  <operator id="3">
    <instruction>Validate each filtered answer by cross-referencing with contextual clues and known facts from the provided data.</instruction>
    <input>filtered_answers</input>
    <output>validated_answers</output>
  </operator>
  <operator id="4">
    <instruction>Ensure that only one answer remains after validation; if multiple remain, apply a tie-breaking rule based on strongest evidence.</instruction>
    <input>validated_answers</input>
    <output>final_answer</output>
  </operator>
  <operator id="5">
    <instruction>Double-check final answer against all prior steps to prevent logical inconsistencies or omissions.</instruction>
    <input>final_answer</input>
    <output>verified_final_answer</output>
  </operator>
  <operator id="6">
    <instruction>Format the verified final answer as a clean, concise response suitable for the task.</instruction>
    <input>verified_final_answer</input>
    <output>output</output>
  </operator>