# Workflow ID: hotpotqa_93_0
# Benchmark: hotpotqa
# Data Indices: [1135, 3537, 1908, 2582]

<operator id="0">
    <instruction>Identify the key elements in the question and context that relate to the answer.</instruction>
    <input>problem</input>
    <output>key_elements</output>
  </operator>
  <operator id="1">
    <instruction>Extract relevant facts from the context that directly address the question.</instruction>
    <input>key_elements</input>
    <output>extracted_facts</output>
  </operator>
  <operator id="2">
    <instruction>Map extracted facts to possible answer candidates using logical reasoning.</instruction>
    <input>extracted_facts</input>
    <output>candidate_answers</output>
  </operator>
  <operator id="3">
    <instruction>Validate each candidate against all provided context to eliminate inconsistencies.</instruction>
    <input>candidate_answers</input>
    <output>validated_answers</output>
  </operator>
  <operator id="4">
    <instruction>Rank validated answers by confidence based on contextual support.</instruction>
    <input>validated_answers</input>
    <output>ranked_answers</output>
  </operator>
  <operator id="5">
    <instruction>Select the highest-confidence answer as the final output.</instruction>
    <input>ranked_answers</input>
    <output>final_answer</output>
  </operator>