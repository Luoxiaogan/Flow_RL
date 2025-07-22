# Workflow ID: drop_609_0
# Benchmark: drop
# Data Indices: [3743, 799, 3839, 2895, 890]

<agent id="1">
    <instruction>Extract all field goal distances from the passage and identify the shortest one.</instruction>
    <input>problem</input>
    <output>shortest_field_goal</output>
  </agent>
  <agent id="2">
    <instruction>Identify all field goal attempts mentioned in the passage and count how many were successful.</instruction>
    <input>problem</input>
    <output>successful_field_goals</output>
  </agent>
  <agent id="3">
    <instruction>Calculate the total number of field goal attempts (successful or missed) by counting instances where a field goal is mentioned.</instruction>
    <input>problem</input>
    <output>total_attempts</output>
  </agent>
  <agent id="4">
    <instruction>Compute the number of converted field goal attempts by subtracting missed attempts from total attempts, if applicable. Otherwise, use the count of successful ones directly.</instruction>
    <input>total_attempts, successful_field_goals</input>
    <output>converted_field_goals</output>
  </agent>
  <agent id="5">
    <instruction>Determine the shortest field goal distance and return it as the final answer for the question.</instruction>
    <input>shortest_field_goal</input>
    <output>final_answer</output>
  </agent>
  <agent id="6">
    <instruction>Verify that the number of converted field goals matches the count of successful attempts from the passage.</instruction>
    <input>successful_field_goals, converted_field_goals</input>
    <output>verification</output>
  </agent>
  <connect from="1" to="5"/>
  <connect from="2" to="4"/>
  <connect from="3" to="4"/>
  <connect from="4" to="6"/>
  <connect from="6" to="5"/>