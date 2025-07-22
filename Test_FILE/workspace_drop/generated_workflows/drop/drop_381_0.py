# Workflow ID: drop_381_0
# Benchmark: drop
# Data Indices: [2271, 1790, 228, 1128, 1165]

<operator id="1">
    <instruction>Identify all relevant events in the passage that involve numerical values related to the question. Focus on specific actions like touchdown passes, field goals, or runs with yardage.</instruction>
    <input>problem</input>
    <output>list_of_events</output>
  </operator>

  <operator id="2">
    <instruction>Filter the list of events to include only those that match the criteria specified in the question—e.g., touchdown passes between 3 and 50 yards, or differences in yardage between two runs by the same player.</instruction>
    <input>list_of_events</input>
    <output>filtered_events</output>
  </operator>

  <operator id="3">
    <instruction>For each filtered event, extract the numeric value (yardage) and store it in a structured format such as a list of integers.</instruction>
    <input>filtered_events</input>
    <output>yardage_values</output>
  </operator>

  <operator id="4">
    <instruction>If the question requires a difference between two values (like two runs by Jacobs), compute the absolute difference between the first and second values in the yardage list.</instruction>
    <input>yardage_values</input>
    <output>difference_or_sum</output>
  </operator>

  <operator id="5">
    <instruction>If the question asks for a total count (e.g., number of TDs in a range), sum up the number of qualifying events or use the length of the yardage list.</instruction>
    <input>yardage_values</input>
    <output>total_or_count</output>
  </operator>

  <operator id="6">
    <instruction>Combine the result from the appropriate operator (either difference_or_sum or total_or_count) based on the nature of the question. If multiple operators are valid, choose the one that matches the exact query structure.</instruction>
    <input>difference_or_sum, total_or_count</input>
    <output>final_answer</output>
  </operator>

  <operator id="7">
    <instruction>Validate the final answer against the original question's intent: ensure it answers exactly what was asked without over- or under-counting.</instruction>
    <input>final_answer</input>
    <output>validated_answer</output>
  </operator>