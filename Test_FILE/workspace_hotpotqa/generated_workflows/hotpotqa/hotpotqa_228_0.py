# Workflow ID: hotpotqa_228_0
# Benchmark: hotpotqa
# Data Indices: [748, 3312, 643, 2044, 3944]

<operator id="0" type="agent">
    <instruction>Think step by step to determine the correct answer. Analyze the input context thoroughly and identify the key facts relevant to the question.</instruction>
  </operator>
  <operator id="1" type="agent">
    <instruction>Verify that all necessary information from the context is used correctly. Ensure no critical detail is overlooked in your reasoning process.</instruction>
  </operator>
  <operator id="2" type="agent">
    <instruction>Check for consistency between the evidence and the conclusion. If any part of the reasoning seems contradictory, re-evaluate it carefully.</instruction>
  </operator>
  <operator id="3" type="agent">
    <instruction>Ensure your final answer directly addresses the question without adding unnecessary details or assumptions.</instruction>
  </operator>
  <operator id="4" type="agent">
    <instruction>Double-check that your answer aligns with the most accurate interpretation of the provided context, especially when multiple interpretations are possible.</instruction>
  </operator>
  <operator id="5" type="agent">
    <instruction>Finalize your response based on the consensus of the previous steps. Confirm that each operator's contribution leads logically to the correct output.</instruction>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>