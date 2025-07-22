# Workflow ID: drop_696_0
# Benchmark: drop
# Data Indices: [1389, 3745, 3910, 3941, 3462]

<start>
    <task>Identify the relevant field goal distances from the passage</task>
    <next>filter_field_goals</next>
  </start>

  <filter_field_goals>
    <task>Extract all field goals and their yardages from the passage</task>
    <next>filter_by_range</next>
  </filter_field_goals>

  <filter_by_range>
    <task>Filter field goals that are between 20 and 30 yards inclusive</task>
    <next>count_filtered</next>
  </filter_by_range>

  <count_filtered>
    <task>Count how many field goals fall in the specified range (20-30 yards)</task>
    <next>output_result</next>
  </count_filtered>

  <output_result>
    <task>Return the final count as the answer</task>
    <next>end</next>
  </output_result>

  <end>
    <output>Final count of field goals between 20 and 30 yards</output>
  </end>