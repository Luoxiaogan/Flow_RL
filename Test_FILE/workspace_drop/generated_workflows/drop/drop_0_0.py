# Workflow ID: drop_0_0
# Benchmark: drop
# Data Indices: [2810, 1349, 1587, 81]

<agent id="1">
        <instruction>Extract all field goal distances from the passage.</instruction>
        <output>list_of_field_goals</output>
    </agent>
    <agent id="2">
        <instruction>Filter field goals that are between 20 and 50 yards inclusive.</instruction>
        <input>list_of_field_goals</input>
        <output>filtered_field_goals</output>
    </agent>
    <agent id="3">
        <instruction>Find the maximum value among the filtered field goals.</instruction>
        <input>filtered_field_goals</input>
        <output>longest_field_goal</output>
    </agent>
    <agent id="4">
        <instruction>Count how many field goals were made in the specified range (20-50 yards).</instruction>
        <input>filtered_field_goals</input>
        <output>count_in_range</output>
    </agent>
    <agent id="5">
        <instruction>Return a tuple containing the count of field goals between 20 and 50 yards and the longest such field goal.</instruction>
        <input>count_in_range, longest_field_goal</input>
        <output>final_answer</output>
    </agent>