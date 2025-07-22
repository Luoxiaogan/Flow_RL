# Workflow ID: drop_357_0
# Benchmark: drop
# Data Indices: [2348, 2590, 3132, 2820]

<node id="1" type="input">
        <prompt>Extract all field goal distances from the passage.</prompt>
    </node>
    <node id="2" type="operator">
        <prompt>Identify and sum only the field goals made by Matt Bryant.</prompt>
    </node>
    <node id="3" type="output">
        <prompt>Return the total yards from Matt Bryant's field goals.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>