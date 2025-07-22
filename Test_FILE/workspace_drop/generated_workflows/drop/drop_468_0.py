# Workflow ID: drop_468_0
# Benchmark: drop
# Data Indices: [2043, 710, 1634, 2606, 3599]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant percentage data from the passage related to the group in question.</instruction>
    </node>
    <node id="3" type="agent">
        <instruction>Calculate the percentage of people who were not part of the specified group by subtracting the given percentage from 100%.</instruction>
    </node>
    <node id="4" type="agent">
        <instruction>Verify the calculation logic and ensure no rounding or arithmetic errors occurred.</instruction>
    </node>
    <node id="5" type="output">
        <data>final_percentage</data>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>