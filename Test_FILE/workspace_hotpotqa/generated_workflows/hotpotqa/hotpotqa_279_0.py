# Workflow ID: hotpotqa_279_0
# Benchmark: hotpotqa
# Data Indices: [1683, 1924, 3752, 3112, 3592]

<operator id="0" type="agent">
    <instruction>Think step by step to identify the core concept in the context that directly answers the question.</instruction>
    <input>context</input>
    <output>core_concept</output>
  </operator>
  <operator id="1" type="agent">
    <instruction>Extract the specific entity or fact from the core concept that matches the question's requirement.</instruction>
    <input>core_concept</input>
    <output>answer_entity</output>
  </operator>
  <operator id="2" type="agent">
    <instruction>Verify the extracted entity against the question to ensure relevance and accuracy.</instruction>
    <input>answer_entity, question</input>
    <output>verified_answer</output>
  </operator>
  <operator id="3" type="agent">
    <instruction>Format the verified answer into a concise, clear response suitable for the final output.</instruction>
    <input>verified_answer</input>
    <output>final_output</output>
  </operator>
  <edge from="0" to="1" />
  <edge from="1" to="2" />
  <edge from="2" to="3" />