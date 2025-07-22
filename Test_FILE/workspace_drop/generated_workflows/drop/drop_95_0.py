# Workflow ID: drop_95_0
# Benchmark: drop
# Data Indices: [203, 270, 803, 3586]

<agent id="1">
    <instruction>Identify the key event or action in the passage that directly answers the question. Focus on specific players, scores, or plays mentioned.</instruction>
    <output>Extract relevant sentence(s) containing the answer to the question.</output>
  </agent>
  <agent id="2">
    <instruction>From the extracted sentence, locate the exact information that answers the question. If multiple candidates exist, select the one that best fits the context of the question.</instruction>
    <output>Provide the direct answer based on the selected information.</output>
  </agent>
  <agent id="3">
    <instruction>Verify the correctness of the answer by cross-referencing with other parts of the passage to ensure no contradictions or misinterpretations.</instruction>
    <output>Confirm if the answer is accurate and consistent with the passage.</output>
  </agent>
  <agent id="4">
    <instruction>If the answer is confirmed, return it as the final output. If not, re-evaluate using the previous agents' outputs to refine the result.</instruction>
    <output>Final answer to the question.</output>
  </agent>
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="3" to="4"/>