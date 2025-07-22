# Workflow ID: hotpotqa_265_0
# Benchmark: hotpotqa
# Data Indices: [1354, 696, 3203, 2637, 2496]

<operator id="0" type="agent">
    <instruction>Identify the key entities and relationships in the problem context. Focus on extracting relevant facts that directly answer the question.</instruction>
  </operator>
  <operator id="1" type="agent">
    <instruction>Verify if the extracted information from operator 0 contains a direct answer to the question. If not, identify what additional information is needed.</instruction>
  </operator>
  <operator id="2" type="agent">
    <instruction>Search for any missing but necessary details in the context that would allow you to resolve the question definitively.</instruction>
  </operator>
  <operator id="3" type="agent">
    <instruction>Combine all verified facts logically to derive the correct answer. Ensure no assumptions are made beyond the provided context.</instruction>
  </operator>
  <operator id="4" type="agent">
    <instruction>Double-check the final answer against the original question to ensure it fully addresses what was asked.</instruction>
  </operator>
  <operator id="5" type="agent">
    <instruction>Output only the final answer as a concise, accurate response based on your reasoning chain.</instruction>
  </operator>