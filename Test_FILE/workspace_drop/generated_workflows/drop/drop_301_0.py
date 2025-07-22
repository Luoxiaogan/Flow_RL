# Workflow ID: drop_301_0
# Benchmark: drop
# Data Indices: [2311, 3763, 1666, 565]

<agent id="1">
    <instruction>Identify the relevant information in the passage related to the question. Focus on specific yardage values mentioned for touchdowns or field goals.</instruction>
    <input>problem</input>
    <output>filtered_data</output>
  </agent>
  
  <agent id="2">
    <instruction>Extract all touchdown runs and their yardages from the filtered data. Only consider plays that are explicitly described as "touchdown runs."</instruction>
    <input>filtered_data</input>
    <output>touchdown_runs</output>
  </agent>
  
  <agent id="3">
    <instruction>From the list of touchdown runs, determine the longest one by comparing yardages.</instruction>
    <input>touchdown_runs</input>
    <output>longest_run</output>
  </agent>
  
  <agent id="4">
    <instruction>Filter the passage to find all field goals made in the second quarter only.</instruction>
    <input>filtered_data</input>
    <output>second_quarter_field_goals</output>
  </agent>
  
  <agent id="5">
    <instruction>Count how many field goals were kicked in the second quarter from the filtered list.</instruction>
    <input>second_quarter_field_goals</input>
    <output>field_goal_count</output>
  </agent>
  
  <agent id="6">
    <instruction>Combine the results from the longest run and the second-quarter field goal count into a single structured output.</instruction>
    <input>longest_run, field_goal_count</input>
    <output>final_answer</output>
  </agent>