# Workflow ID: drop_765_0
# Benchmark: drop
# Data Indices: [3897, 91, 2108, 3875, 400]

<operator id="1">
        <instruction>Identify the relevant statistics for each player mentioned in the passage related to their receiving yards and number of catches.</instruction>
        <input>problem</input>
        <output>player_stats</output>
    </operator>
    
    <operator id="2">
        <instruction>Calculate the average yards per catch for Tyler by dividing total receiving yards by number of receptions.</instruction>
        <input>player_stats</input>
        <output>taylor_avg</output>
    </operator>
    
    <operator id="3">
        <instruction>Calculate the average yards per catch for Clark by dividing total receiving yards by number of receptions.</instruction>
        <input>player_stats</input>
        <output>clark_avg</output>
    </operator>
    
    <operator id="4">
        <instruction>Compare the averages of Tyler and Clark to determine who had a higher average.</instruction>
        <input>taylor_avg, clark_avg</input>
        <output>higher_avg_player</output>
    </operator>
    
    <operator id="5">
        <instruction>Return the name of the player with the higher average yards per caught pass.</instruction>
        <input>higher_avg_player</input>
        <output>final_answer</output>
    </operator>