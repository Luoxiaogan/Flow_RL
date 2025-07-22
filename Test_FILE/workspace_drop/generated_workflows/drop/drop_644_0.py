# Workflow ID: drop_644_0
# Benchmark: drop
# Data Indices: [2180, 297, 1694, 3987]

<node id="1" type="input">
        <param name="problem" />
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract all field goal distances from the passage. Focus only on explicit yardage values mentioned in the context of field goals.</instruction>
        <input>problem</input>
        <output>field_goal_distances</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Identify the longest field goal distance from the list of extracted distances.</instruction>
        <input>field_goal_distances</input>
        <output>longest_field_goal</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Identify the shortest field goal distance from the list of extracted distances.</instruction>
        <input>field_goal_distances</input>
        <output>shortest_field_goal</output>
    </node>
    
    <node id="5" type="agent">
        <instruction>Calculate the difference between the longest and shortest field goal distances.</instruction>
        <input>
            <param name="longest">longest_field_goal</param>
            <param name="shortest">shortest_field_goal</param>
        </input>
        <output>difference</output>
    </node>
    
    <node id="6" type="agent">
        <instruction>Determine how many field goals were 50 yards or more by counting those in the list that meet or exceed 50.</instruction>
        <input>field_goal_distances</input>
        <output>count_50_plus</output>
    </node>
    
    <node id="7" type="agent">
        <instruction>Return the final answer based on the question asked: either the count of field goals ≥50 yards, or the yardage difference between longest and shortest, depending on the question.</instruction>
        <input>
            <param name="count_50_plus">count_50_plus</param>
            <param name="difference">difference</param>
        </input>
        <output>final_answer</output>
    </node>
    
    <node id="8" type="output">
        <param name="result" value="final_answer" />
    </node>