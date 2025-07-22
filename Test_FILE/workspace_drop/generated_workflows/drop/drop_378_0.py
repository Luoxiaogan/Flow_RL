# Workflow ID: drop_378_0
# Benchmark: drop
# Data Indices: [3441, 3416, 703, 3058]

<node id="1">
        <instruction>Extract all field goal distances from the passage.</instruction>
        <input>problem</input>
        <output>field_goals</output>
    </node>
    <node id="2">
        <instruction>Identify the longest field goal among the extracted values.</instruction>
        <input>field_goals</input>
        <output>longest_field_goal</output>
    </node>
    <node id="3">
        <instruction>Return the yardage of the longest field goal as the final answer.</instruction>
        <input>longest_field_goal</input>
        <output>final_answer</output>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>