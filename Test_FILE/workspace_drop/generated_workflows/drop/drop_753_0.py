# Workflow ID: drop_753_0
# Benchmark: drop
# Data Indices: [2190, 3904, 2686, 3670]

<node id="1" type="input">
        <prompt>Read the passage carefully and identify all numerical values related to field goals.</prompt>
    </node>
    <node id="2" type="operator">
        <prompt>Extract each field goal distance mentioned in the passage. List them in order of appearance.</prompt>
    </node>
    <node id="3" type="operator">
        <prompt>Compare the distances to determine the largest value among them.</prompt>
    </node>
    <node id="4" type="output">
        <prompt>Return the longest field goal distance identified from the passage.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>