# Workflow ID: drop_294_0
# Benchmark: drop
# Data Indices: [2362, 982, 1070, 1957, 3935]

<start>
    <operator name="extract_field_goals" instruction="Identify all field goals mentioned in the passage and their yardages. Think step by step to ensure no field goal is missed."/>
    <operator name="find_longest" instruction="From the list of field goals, determine the one with the maximum yardage. Consider each field goal's distance carefully to avoid errors."/>
    <operator name="validate" instruction="Double-check that the longest field goal identified matches the highest yardage in the data. Ensure no other field goal exceeds it."/>
    <operator name="return_result" instruction="Return the yardage of the longest field goal as the final answer. Make sure the output is a single numeric value."/>
  </start>
  <connect from="extract_field_goals" to="find_longest"/>
  <connect from="find_longest" to="validate"/>
  <connect from="validate" to="return_result"/>