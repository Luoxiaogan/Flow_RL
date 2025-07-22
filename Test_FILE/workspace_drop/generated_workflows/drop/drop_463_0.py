# Workflow ID: drop_463_0
# Benchmark: drop
# Data Indices: [1976, 2870, 1072, 1900, 422]

<agent id="1">
        <instruction>Identify all scoring plays in the passage and extract yardage for field goals and touchdowns.</instruction>
        <output>list_of_plays</output>
    </agent>
    
    <agent id="2">
        <instruction>From the list of plays, filter only field goals and determine the shortest one.</instruction>
        <input>list_of_plays</input>
        <output>shortest_field_goal_yardage</output>
    </agent>
    
    <agent id="3">
        <instruction>From the list of plays, identify which player scored the first touchdown of the game.</instruction>
        <input>list_of_plays</input>
        <output>first_touchdown_player</output>
    </agent>
    
    <agent id="4">
        <instruction>Find the total yards completed by a specific quarterback mentioned in the passage.</instruction>
        <input>list_of_plays</input>
        <output>quarterback_pass_yards</output>
    </agent>
    
    <agent id="5">
        <instruction>Determine how many touchdowns a specific player (e.g., Greg Olsen) scored based on the passage.</instruction>
        <input>list_of_plays</input>
        <output>player_touchdowns</output>
    </agent>
    
    <agent id="6">
        <instruction>Check if any field goal tied or broke a record — this helps validate unique events.</instruction>
        <input>list_of_plays</input>
        <output>record_breaking_field_goal</output>
    </agent>
    
    <agent id="7">
        <instruction>Aggregate results from all agents to produce final answer(s) for each question.</instruction>
        <input>shortest_field_goal_yardage, first_touchdown_player, quarterback_pass_yards, player_touchdowns, record_breaking_field_goal</input>
        <output>final_answer</output>
    </agent>