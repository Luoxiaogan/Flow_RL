# Workflow ID: drop_219_0
# Benchmark: drop
# Data Indices: [2047, 574, 3118, 255, 3899]

<operator id="0">
    <instruction>Understand the question and identify the key information needed to solve it.</instruction>
    <input>problem</input>
    <output>question_analysis</output>
  </operator>
  <operator id="1">
    <instruction>Extract relevant numerical data from the passage that directly relates to the question.</instruction>
    <input>problem</input>
    <output>numerical_data</output>
  </operator>
  <operator id="2">
    <instruction>Perform necessary calculations based on the extracted data to answer the question step by step.</instruction>
    <input>numerical_data, question_analysis</input>
    <output>calculation_result</output>
  </operator>
  <operator id="3">
    <instruction>Verify the calculation logic and ensure the final answer matches the question's requirement.</instruction>
    <input>calculation_result</input>
    <output>verified_answer</output>
  </operator>
  <operator id="4">
    <instruction>Format the verified answer appropriately for output (e.g., number, percentage, etc.).</instruction>
    <input>verified_answer</input>
    <output>final_output</output>
  </operator>
  <edge from="0" to="2"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>