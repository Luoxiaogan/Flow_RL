# Workflow ID: drop_290_0
# Benchmark: drop
# Data Indices: [3617, 3748, 3947, 3859]

<operator id="1">
        <instruction>Identify the key events in the passage that relate to scoring plays.</instruction>
        <input>passage</input>
        <output>scoring_events</output>
    </operator>
    
    <operator id="2">
        <instruction>Determine which scoring event was a touchdown reception and note the yardage.</instruction>
        <input>scoring_events</input>
        <output>touchdown_receptions</output>
    </operator>
    
    <operator id="3">
        <instruction>Among all touchdown receptions, find the one with the longest yardage.</instruction>
        <input>touchdown_receptions</input>
        <output>longest_touchdown_reception</output>
    </operator>
    
    <operator id="4">
        <instruction>Extract the player who scored the longest touchdown reception from the event details.</instruction>
        <input>longest_touchdown_reception</input>
        <output>player_scored_longest_td</output>
    </operator>
    
    <operator id="5">
        <instruction>Return the name of the player who scored the longest touchdown reception.</instruction>
        <input>player_scored_longest_td</input>
        <output>final_answer</output>
    </operator>