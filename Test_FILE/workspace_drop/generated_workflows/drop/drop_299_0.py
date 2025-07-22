# Workflow ID: drop_299_0
# Benchmark: drop
# Data Indices: [2769, 3164, 3278, 495]

<operator id="0">
        <instruction>Identify the key scoring events in the game based on the passage.</instruction>
        <input>problem</input>
        <output>scoring_events</output>
    </operator>
    <operator id="1">
        <instruction>From the scoring events, extract only the touchdowns scored by the Broncos.</instruction>
        <input>scoring_events</input>
        <output>broncos_touchdowns</output>
    </operator>
    <operator id="2">
        <instruction>Count the number of times the Broncos scored a touchdown.</instruction>
        <input>broncos_touchdowns</input>
        <output>num_touchdowns</output>
    </operator>
    <operator id="3">
        <instruction>Check if there were any field goals scored by the Broncos.</instruction>
        <input>scoring_events</input>
        <output>field_goals</output>
    </operator>
    <operator id="4">
        <instruction>Count the number of field goals made by the Broncos.</instruction>
        <input>field_goals</input>
        <output>num_field_goals</output>
    </operator>
    <operator id="5">
        <instruction>Add the number of touchdowns and field goals to get total scores.</instruction>
        <input>num_touchdowns, num_field_goals</input>
        <output>total_scores</output>
    </operator>
    <operator id="6">
        <instruction>Return the total number of times the Broncos scored in the game.</instruction>
        <input>total_scores</input>
        <output>final_answer</output>
    </operator>
    <connection from="0" to="1"/>
    <connection from="0" to="3"/>
    <connection from="1" to="2"/>
    <connection from="3" to="4"/>
    <connection from="2" to="5"/>
    <connection from="4" to="5"/>
    <connection from="5" to="6"/>