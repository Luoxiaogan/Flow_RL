# Workflow ID: hotpotqa_130_0
# Benchmark: hotpotqa
# Data Indices: [711, 189, 2180, 13, 3277]

<operator id="0">
    <instruction>Understand the question and identify key elements to determine the answer.</instruction>
    <input>problem</input>
    <output>key_elements</output>
  </operator>
  <operator id="1">
    <instruction>Extract relevant context information that directly relates to the key elements identified in step 0.</instruction>
    <input>key_elements, context</input>
    <output>relevant_context</output>
  </operator>
  <operator id="2">
    <instruction>Compare and analyze the extracted context to evaluate which option fits the criteria in the question.</instruction>
    <input>relevant_context</input>
    <output>comparison_result</output>
  </operator>
  <operator id="3">
    <instruction>Verify the comparison result against known definitions or properties related to the entities involved.</instruction>
    <input>comparison_result</input>
    <output>verification_result</output>
  </operator>
  <operator id="4">
    <instruction>Generate a concise final answer based on the verified result, ensuring it aligns with the original question.</instruction>
    <input>verification_result</input>
    <output>final_answer</output>
  </operator>
  <connect from="0" to="1"/>
  <connect from="1" to="2"/>
  <connect from="2" to="3"/>
  <connect from="3" to="4"/>