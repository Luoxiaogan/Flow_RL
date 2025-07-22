# Workflow ID: drop_322_0
# Benchmark: drop
# Data Indices: [2053, 3905, 956, 627, 241]

<agent id="1">
    <instruction>Identify the relevant information in the passage related to the question. Extract all instances where the subject of the question is mentioned in connection with the quantity being asked.</instruction>
    <input>problem</input>
    <output>extracted_info</output>
  </agent>
  <agent id="2">
    <instruction>From the extracted information, list all numerical values or counts directly tied to the subject. If multiple events are described, ensure each instance is counted appropriately.</instruction>
    <input>extracted_info</input>
    <output>count_list</output>
  </agent>
  <agent id="3">
    <instruction>Filter the count list to include only those that match the condition specified in the question (e.g., field goals over a certain yardage, touchdowns in a specific time frame).</instruction>
    <input>count_list</input>
    <output>filtered_values</output>
  </agent>
  <agent id="4">
    <instruction>Sum up all filtered values if the question asks for a total. If it's a single value, return that value directly.</instruction>
    <input>filtered_values</input>
    <output>final_answer</output>
  </agent>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>