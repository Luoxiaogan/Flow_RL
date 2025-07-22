# Workflow ID: hotpotqa_326_0
# Benchmark: hotpotqa
# Data Indices: [1533, 832, 3721, 2245, 3642]

<operator id="1" type="agent">
    <instruction>Think step by step to identify the key concept from the context that directly answers the question.</instruction>
    <input>problem</input>
    <output>key_concept</output>
  </operator>
  <operator id="2" type="agent">
    <instruction>Based on the key concept, determine the precise term or phrase used in the context that matches the question's requirement.</instruction>
    <input>key_concept</input>
    <output>precise_term</output>
  </operator>
  <operator id="3" type="agent">
    <instruction>Verify that the precise term aligns with both the question and the historical context provided.</instruction>
    <input>precise_term</input>
    <output>verification_result</output>
  </operator>
  <operator id="4" type="agent">
    <instruction>Ensure the final answer is concise, accurate, and matches the expected format of the question.</instruction>
    <input>verification_result</input>
    <output>final_answer</output>
  </operator>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>