# Workflow ID: hotpotqa_448_0
# Benchmark: hotpotqa
# Data Indices: [2946, 2701, 1554, 1471]

<agent id="1">
    <instruction>Identify the key entity in the question and locate its relevant context.</instruction>
    <output>Extracted entity and related context.</output>
  </agent>
  <agent id="2">
    <instruction>Process the extracted context to isolate the specific detail required by the question.</instruction>
    <output>Isolated answer component from context.</output>
  </agent>
  <agent id="3">
    <instruction>Validate the isolated component against known facts or definitions to ensure accuracy.</instruction>
    <output>Validated answer with confidence level.</output>
  </agent>
  <agent id="4">
    <instruction>Combine validated components into a final, coherent response that directly answers the question.</instruction>
    <output>Final answer string formatted for clarity and correctness.</output>
  </agent>