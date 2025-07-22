# Workflow ID: drop_541_0
# Benchmark: drop
# Data Indices: [1569, 3972, 1203, 3717, 2454]

<node id="1" type="input">
        <prompt>Extract all field goal distances from the passage.</prompt>
        <output>list_of_field_goals</output>
    </node>
    
    <node id="2" type="operator">
        <prompt>Identify the longest field goal among all recorded ones.</prompt>
        <input>list_of_field_goals</input>
        <output>longest_field_goal</output>
    </node>
    
    <node id="3" type="operator">
        <prompt>Identify the shortest field goal among all recorded ones.</prompt>
        <input>list_of_field_goals</input>
        <output>shortest_field_goal</output>
    </node>
    
    <node id="4" type="operator">
        <prompt>Calculate the difference between the longest and shortest field goals.</prompt>
        <input>longest_field_goal, shortest_field_goal</input>
        <output>difference</output>
    </node>
    
    <node id="5" type="output">
        <prompt>Return the calculated difference as the final answer.</prompt>
        <input>difference</input>
        <output>final_answer</output>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="1" to="3"/>
    <edge from="2" to="4"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>