# Workflow ID: drop_169_0
# Benchmark: drop
# Data Indices: [230, 697, 3820, 3112]

<node id="1" type="input">
        <param name="problem">self.problem</param>
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract all field goal distances mentioned in the passage. Focus only on numerical values associated with field goals.</instruction>
        <param name="input">1</param>
        <output>field_goals</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>From the list of field goals, identify the maximum value. This represents the longest field goal.</instruction>
        <param name="input">2</param>
        <output>longest_field_goal</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Determine if the question asks for a specific player's longest field goal or just the overall longest. If specific, filter by that player; otherwise, use the global maximum.</instruction>
        <param name="input">3</param>
        <output>final_answer</output>
    </node>
    
    <node id="5" type="output">
        <param name="answer">4</param>
    </node>