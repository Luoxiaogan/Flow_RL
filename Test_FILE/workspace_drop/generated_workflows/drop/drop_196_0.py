# Workflow ID: drop_196_0
# Benchmark: drop
# Data Indices: [3169, 1282, 1787, 734, 3277]

<node id="1" type="input">
        <prompt>Understand the question and extract relevant data from the passage.</prompt>
    </node>
    <node id="2" type="process">
        <prompt>Identify all instances of the specified event (e.g., touchdown passes, field goals) and their yardages.</prompt>
    </node>
    <node id="3" type="process">
        <prompt>Apply comparison logic (e.g., difference between two values, find maximum, count below threshold).</prompt>
    </node>
    <node id="4" type="output">
        <prompt>Return the final numerical answer based on the processed information.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>