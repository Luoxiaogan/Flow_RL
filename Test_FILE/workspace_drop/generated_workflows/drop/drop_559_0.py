# Workflow ID: drop_559_0
# Benchmark: drop
# Data Indices: [2539, 932, 2034, 3436, 2234]

<operator id="0">
    <instruction>Extract relevant data from the passage that answers the question.</instruction>
    <input>problem</input>
    <output>filtered_data</output>
  </operator>
  <operator id="1">
    <instruction>Identify the key elements in the filtered data that directly relate to the question.</instruction>
    <input>filtered_data</input>
    <output>key_elements</output>
  </operator>
  <operator id="2">
    <instruction>Process the key elements to compute or determine the answer step by step.</instruction>
    <input>key_elements</input>
    <output>intermediate_result</output>
  </operator>
  <operator id="3">
    <instruction>Verify the intermediate result against all provided information to ensure accuracy.</instruction>
    <input>intermediate_result, filtered_data</input>
    <output>final_answer</output>
  </operator>
  <operator id="4">
    <instruction>Format the final answer in a clear and concise manner for output.</instruction>
    <input>final_answer</input>
    <output>formatted_output</output>
  </operator>
  <connection from="0" to="1"/>
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="3" to="4"/>