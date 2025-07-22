# Workflow ID: hotpotqa_45_0
# Benchmark: hotpotqa
# Data Indices: [2282, 2656, 561, 3057]

<agent id="1" type="reasoning">
    <instruction>Think step by step to identify the key elements of the problem. Break down the question and extract relevant context.</instruction>
  </agent>
  <agent id="2" type="search">
    <instruction>Based on the reasoning from agent 1, locate the specific entity or fact in the provided context that answers the question.</instruction>
  </agent>
  <agent id="3" type="verification">
    <instruction>Verify the answer from agent 2 against all available context to ensure accuracy and avoid false positives.</instruction>
  </agent>
  <agent id="4" type="validation">
    <instruction>Check if the verified answer matches the expected format or structure required by the question (e.g., number, name, code).</instruction>
  </agent>
  <agent id="5" type="output">
    <instruction>Finalize the answer based on validation. If any step fails, return "No valid answer found". Otherwise, return the correct answer.</instruction>
  </agent>
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="3" to="4"/>
  <connection from="4" to="5"/>