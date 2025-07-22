# Workflow ID: drop_156_0
# Benchmark: drop
# Data Indices: [2605, 3876, 3460, 2639, 271]

<node id="1" type="input">
        <prompt>Read the passage carefully and identify all scoring events (touchdowns, field goals, safeties).</prompt>
    </node>
    
    <node id="2" type="process">
        <prompt>Extract each scoring event: note the player, type of score, and time (quarter) it occurred.</prompt>
    </node>
    
    <node id="3" type="process">
        <prompt>Count touchdowns separately from field goals and safeties to ensure accuracy.</prompt>
    </node>
    
    <node id="4" type="process">
        <prompt>Sum all touchdown scores from both teams across all quarters.</prompt>
    </node>
    
    <node id="5" type="output">
        <prompt>Return the total number of touchdowns scored in the game.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>