# Workflow ID: hotpotqa_282_0
# Benchmark: hotpotqa
# Data Indices: [3539, 1211, 3216, 3214, 1819]

<operator id="1">
    <instruction>Identify the key entities and relationships in the problem context that are relevant to solving the question.</instruction>
    <input>problem</input>
    <output>entity_relations</output>
  </operator>
  
  <operator id="2">
    <instruction>Extract specific details from the context that directly answer the question, focusing on named individuals, dates, and affiliations.</instruction>
    <input>entity_relations</input>
    <output>extracted_details</output>
  </operator>
  
  <operator id="3">
    <instruction>Verify if the extracted details form a coherent chain of evidence leading to the correct answer. If not, identify missing links or ambiguous terms.</instruction>
    <input>extracted_details</input>
    <output>coherence_check</output>
  </operator>
  
  <operator id="4">
    <instruction>If coherence is confirmed, synthesize the final answer. Otherwise, refine the search by re-examining related context for missing clues.</instruction>
    <input>coherence_check</input>
    <output>final_answer</output>
  </operator>