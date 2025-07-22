# Workflow ID: hotpotqa_332_0
# Benchmark: hotpotqa
# Data Indices: [594, 2579, 3678, 3914]

<agent id="1">
    <instruction>Identify the key elements in the question and locate the relevant context that directly answers it.</instruction>
    <input>problem</input>
    <output>candidate_answer</output>
  </agent>
  <agent id="2">
    <instruction>Verify the candidate answer by cross-referencing with other parts of the context to ensure accuracy and avoid false positives.</instruction>
    <input>candidate_answer, context</input>
    <output>verified_answer</output>
  </agent>
  <agent id="3">
    <instruction>Check for any ambiguity or missing information in the verified answer. If necessary, re-evaluate the context for alternative interpretations.</instruction>
    <input>verified_answer, context</input>
    <output>final_answer</output>
  </agent>
  <agent id="4">
    <instruction>Format the final answer to match the required output style (e.g., plain text, JSON, etc.).</instruction>
    <input>final_answer</input>
    <output>formatted_output</output>
  </agent>
  <link from="1" to="2"/>
  <link from="2" to="3"/>
  <link from="3" to="4"/>