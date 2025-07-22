# Workflow ID: drop_640_0
# Benchmark: drop
# Data Indices: [2268, 2925, 2703, 3990]

<agent id="1">
        <instruction>Extract all field goal distances from the passage.</instruction>
        <output>list of field goal yardages</output>
    </agent>
    <agent id="2">
        <instruction>Filter the list to include only field goals from the first half.</instruction>
        <output>first_half_field_goals</output>
    </agent>
    <agent id="3">
        <instruction>Sum the yardages of the first-half field goals.</instruction>
        <output>total_first_half_yards</output>
    </agent>
    <agent id="4">
        <instruction>Return the total yards of field goals in the first half.</instruction>
        <output>final_answer</output>
    </agent>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>