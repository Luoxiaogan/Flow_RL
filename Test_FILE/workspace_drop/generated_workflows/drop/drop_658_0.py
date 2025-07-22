# Workflow ID: drop_658_0
# Benchmark: drop
# Data Indices: [2571, 1807, 698, 3439, 3167]

<node id="1" type="input">
        <param name="problem">self.problem</param>
    </node>
    
    <node id="2" type="agent">
        <instruction>Read the passage carefully and identify all players who scored touchdowns. Note the yardage of each touchdown.</instruction>
        <input>1</input>
        <output>player_touchdowns</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Filter the list of players to include only those whose touchdowns were 30 yards or more. Be precise with the yardage values from the passage.</instruction>
        <input>2</input>
        <output>qualified_players</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Verify that each player in the qualified list indeed scored a touchdown of at least 30 yards by cross-checking their name and yardage in the passage.</instruction>
        <input>3</input>
        <output>verified_list</output>
    </node>
    
    <node id="5" type="output">
        <input>4</input>
        <output>final_answer</output>
    </node>