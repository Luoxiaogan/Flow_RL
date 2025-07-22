# Workflow ID: hotpotqa_109_0
# Benchmark: hotpotqa
# Data Indices: [2001, 2711, 324, 2984, 1798]

<operator id="1">
    <instruction>Identify the key entity in the question and locate its relevant context.</instruction>
    <input>problem</input>
    <output>entity_context</output>
  </operator>
  
  <operator id="2">
    <instruction>Extract specific details from the context that directly answer the question.</instruction>
    <input>entity_context</input>
    <output>relevant_details</output>
  </operator>
  
  <operator id="3">
    <instruction>Verify the extracted details against the question to ensure accuracy.</instruction>
    <input>relevant_details</input>
    <output>verified_answer</output>
  </operator>
  
  <operator id="4">
    <instruction>Format the verified answer into a clear, concise response.</instruction>
    <input>verified_answer</input>
    <output>final_output</output>
  </operator>