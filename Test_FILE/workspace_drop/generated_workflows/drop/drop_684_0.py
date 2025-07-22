# Workflow ID: drop_684_0
# Benchmark: drop
# Data Indices: [2973, 1152, 1321, 1991]

<operator id="1">
        <instruction>Identify the key events in the passage that involve scoring plays, such as touchdowns and field goals. List them in chronological order.</instruction>
        <input>problem</input>
        <output>event_list</output>
    </operator>

    <operator id="2">
        <instruction>From the event list, extract only the touchdown scores and their associated players or teams.</instruction>
        <input>event_list</input>
        <output>touchdowns</output>
    </operator>

    <operator id="3">
        <instruction>Determine the last touchdown scored in the game by looking at the final entry in the sorted touchdown list.</instruction>
        <input>touchdowns</input>
        <output>last_touchdown</output>
    </operator>

    <operator id="4">
        <instruction>Return the name of the player who scored the last touchdown based on the extracted information.</instruction>
        <input>last_touchdown</input>
        <output>final_answer</output>
    </operator>

    <connect from="1" to="2"/>
    <connect from="2" to="3"/>
    <connect from="3" to="4"/>