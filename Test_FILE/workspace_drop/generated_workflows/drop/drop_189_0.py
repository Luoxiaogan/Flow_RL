# Workflow ID: drop_189_0
# Benchmark: drop
# Data Indices: [3151, 984, 1104, 2734, 1315]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="process">
        <instruction>Extract relevant numerical values from the passage for comparison.</instruction>
    </node>
    <node id="3" type="process">
        <instruction>Calculate the difference between the two percentages.</instruction>
    </node>
    <node id="4" type="output">
        <instruction>Return the percentage difference as a numeric value.</instruction>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>