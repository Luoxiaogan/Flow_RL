# Workflow ID: drop_15_0
# Benchmark: drop
# Data Indices: [1705, 2317, 2945, 2552]

<start>
        <task>Extract question and passage from input</task>
        <next>identify_key_events</next>
    </start>

    <node id="identify_key_events">
        <task>Identify all scoring events (touchdowns, field goals, etc.) in chronological order</task>
        <next>locate_first_touchdown</next>
    </node>

    <node id="locate_first_touchdown">
        <task>Find the first touchdown scored in the game based on event sequence</task>
        <next>validate_answer</next>
    </node>

    <node id="validate_answer">
        <task>Verify that the identified touchdown scorer is correct by cross-referencing with team names and play details</task>
        <next>return_result</next>
    </node>

    <node id="return_result">
        <task>Return the name of the player who scored the first touchdown</task>
        <next>end</next>
    </node>

    <end>
        <output>Answer to the question: Who scored the first touchdown of the game?</output>
    </end>