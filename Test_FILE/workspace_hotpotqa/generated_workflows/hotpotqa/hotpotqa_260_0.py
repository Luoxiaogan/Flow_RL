# Workflow ID: hotpotqa_260_0
# Benchmark: hotpotqa
# Data Indices: [1824, 950, 1468, 3278]

<operator id="0" type="agent">
    <instruction>Think step by step to identify the key information needed to solve the problem.</instruction>
  </operator>
  <operator id="1" type="agent">
    <instruction>Extract and verify the relevant facts from the context that directly answer the question.</instruction>
  </operator>
  <operator id="2" type="agent">
    <instruction>Use logical reasoning to connect the extracted facts into a coherent solution.</instruction>
  </operator>
  <operator id="3" type="agent">
    <instruction>Validate the solution against all provided context to ensure accuracy.</instruction>
  </operator>
  <operator id="4" type="agent">
    <instruction>Refine the final answer for clarity and correctness based on validation.</instruction>
  </operator>
  <operator id="5" type="agent">
    <instruction>Ensure the output format matches the required structure without any problem-specific details.</instruction>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>