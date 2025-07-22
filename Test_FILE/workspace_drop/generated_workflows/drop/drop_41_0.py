# Workflow ID: drop_41_0
# Benchmark: drop
# Data Indices: [3225, 2880, 3766, 1252]

<node id="1" type="input">
        <prompt>Extract all touchdown-scoring plays from the passage.</prompt>
    </node>
    <node id="2" type="process">
        <prompt>Identify the players who scored touchdowns in the first half based on the extracted plays.</prompt>
    </node>
    <node id="3" type="filter">
        <prompt>Filter out any touchdowns that occurred in the second half or later.</prompt>
    </node>
    <node id="4" type="output">
        <prompt>Return the list of players who scored touchdowns in the first half.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>