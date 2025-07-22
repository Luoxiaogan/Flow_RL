# Workflow ID: hotpotqa_311_0
# Benchmark: hotpotqa
# Data Indices: [3936, 2538, 1261, 1718]

<operator id="0">
    <instruction>Identify the key entities and relationships in the problem. Focus on the main subject and its connections.</instruction>
    <input>problem</input>
    <output>entity_relationships</output>
  </operator>
  <operator id="1">
    <instruction>Extract specific details relevant to the question from the context. Filter out unrelated information.</instruction>
    <input>entity_relationships</input>
    <output>filtered_details</output>
  </operator>
  <operator id="2">
    <instruction>Map the extracted details to the required answer format. Ensure logical consistency and completeness.</instruction>
    <input>filtered_details</input>
    <output>answer_format</output>
  </operator>
  <operator id="3">
    <instruction>Validate the answer against all provided context to ensure accuracy and avoid contradictions.</instruction>
    <input>answer_format</input>
    <output>validated_answer</output>
  </operator>
  <operator id="4">
    <instruction>Refine the answer for clarity, conciseness, and correctness based on validation results.</instruction>
    <input>validated_answer</input>
    <output>final_answer</output>
  </operator>