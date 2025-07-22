# Workflow ID: drop_503_0
# Benchmark: drop
# Data Indices: [2110, 3857, 3429, 2928, 92]

<agent id="1" type="extract">
    <instruction>Extract the relevant numerical data from the passage related to the question.</instruction>
    <input>problem</input>
    <output>extracted_data</output>
  </agent>

  <agent id="2" type="process">
    <instruction>Process the extracted data to compute the required value based on the question's logic.</instruction>
    <input>extracted_data</input>
    <output>computed_value</output>
  </agent>

  <agent id="3" type="validate">
    <instruction>Verify that the computed value matches the expected answer by cross-checking with the passage context.</instruction>
    <input>computed_value, problem</input>
    <output>validated_answer</output>
  </agent>

  <agent id="4" type="ensemble">
    <instruction>Combine results from multiple agents if needed to ensure accuracy, especially when ambiguity exists in the passage.</instruction>
    <input>validated_answer</input>
    <output>final_answer</output>
  </agent>

  <agent id="5" type="format">
    <instruction>Format the final answer as a clean integer or string, ready for output.</instruction>
    <input>final_answer</input>
    <output>formatted_output</output>
  </agent>

  <edge from="1" to="2" />
  <edge from="2" to="3" />
  <edge from="3" to="4" />
  <edge from="4" to="5" />