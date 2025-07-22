# Workflow ID: drop_353_0
# Benchmark: drop
# Data Indices: [353, 3456, 679, 1791]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities and relationships.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant facts from the passage related to the question. Focus on chronological order, quantities, or comparisons as needed.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Determine the correct answer by analyzing the extracted facts step-by-step. Avoid assumptions; rely only on explicit information.</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Return the final answer based on the analysis. Ensure it directly addresses the question.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>