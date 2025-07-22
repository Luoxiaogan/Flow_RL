# Workflow ID: drop_109_0
# Benchmark: drop
# Data Indices: [3793, 1743, 1534, 18]

<node id="1" type="input">
        <prompt>Extract the relevant information from the passage to answer the question.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Identify all touchdown passes thrown by Garrard in the passage. List each one with its yardage.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Count the total number of touchdown passes attributed to Garrard based on the list from node 2.</prompt>
    </node>
    <node id="4" type="output">
        <prompt>Return the total number of touchdown passes thrown by Garrard.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>