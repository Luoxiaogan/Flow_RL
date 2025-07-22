# Workflow ID: drop_303_0
# Benchmark: drop
# Data Indices: [99, 616, 2191, 3384, 1724]

<agent id="1" type="extract">
        <instruction>Identify all players who threw touchdown passes in the passage and note the length of each pass.</instruction>
    </agent>
    <agent id="2" type="filter">
        <instruction>From the extracted data, filter only the touchdown passes and their lengths.</instruction>
    </agent>
    <agent id="3" type="sort">
        <instruction>Sort the filtered touchdown passes by length in descending order to identify the longest ones.</instruction>
    </agent>
    <agent id="4" type="select">
        <instruction>Select the third longest touchdown pass from the sorted list.</instruction>
    </agent>
    <agent id="5" type="output">
        <instruction>Return the player who threw the third longest touchdown pass.</instruction>
    </agent>
    <connection from="1" to="2"/>
    <connection from="2" to="3"/>
    <connection from="3" to="4"/>
    <connection from="4" to="5"/>