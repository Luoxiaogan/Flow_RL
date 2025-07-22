# Workflow ID: drop_418_0
# Benchmark: drop
# Data Indices: [2781, 485, 3263, 3154]

<operator id="0">
    <instruction>Understand the question and identify key elements to extract from the passage.</instruction>
    <input>problem</input>
    <output>key_elements</output>
  </operator>
  <operator id="1">
    <instruction>Extract relevant numerical data from the passage based on the key elements identified.</instruction>
    <input>key_elements, passage</input>
    <output>numerical_data</output>
  </operator>
  <operator id="2">
    <instruction>Apply logical reasoning to compare or calculate values as required by the question.</instruction>
    <input>numerical_data</input>
    <output>result</output>
  </operator>
  <operator id="3">
    <instruction>Verify the result against the passage to ensure accuracy and completeness.</instruction>
    <input>result, passage</input>
    <output>final_answer</output>
  </operator>
  <operator id="4">
    <instruction>Format the final answer in a clear and concise manner for output.</instruction>
    <input>final_answer</input>
    <output>formatted_output</output>
  </operator>