# Workflow ID: hotpotqa_236_0
# Benchmark: hotpotqa
# Data Indices: [399, 3120, 232, 2994, 3343]

<operator id="1">
    <instruction>Identify the key elements in the question and match them with the relevant context provided.</instruction>
    <input>problem</input>
    <output>filtered_context</output>
  </operator>
  <operator id="2">
    <instruction>Extract the specific answer from the filtered context by focusing on the direct relationship between the subject and the required information.</instruction>
    <input>filtered_context</input>
    <output>candidate_answer</output>
  </operator>
  <operator id="3">
    <instruction>Verify the candidate answer against the full context to ensure accuracy and relevance to the question asked.</instruction>
    <input>candidate_answer, filtered_context</input>
    <output>verified_answer</output>
  </operator>
  <operator id="4">
    <instruction>Format the verified answer into a concise and clear response that directly answers the original question.</instruction>
    <input>verified_answer</input>
    <output>final_answer</output>
  </operator>