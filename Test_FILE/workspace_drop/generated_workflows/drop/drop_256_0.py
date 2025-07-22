# Workflow ID: drop_256_0
# Benchmark: drop
# Data Indices: [2102, 1304, 854, 141]

<node id="1" type="input">
        <prompt>Read the passage carefully and identify all relevant numerical data related to the question.</prompt>
    </node>
    <node id="2" type="process">
        <prompt>Extract all touchdown pass lengths from the passage. If no touchdown passes are mentioned, return 0.</prompt>
    </node>
    <node id="3" type="process">
        <prompt>If any touchdown passes were found, determine the shortest one by comparing values.</prompt>
    </node>
    <node id="4" type="output">
        <prompt>Return the length of the shortest touchdown pass. If no touchdown passes exist, return 0.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>