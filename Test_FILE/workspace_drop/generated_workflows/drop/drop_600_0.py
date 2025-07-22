# Workflow ID: drop_600_0
# Benchmark: drop
# Data Indices: [2140, 603, 1169, 2123]

<node id="1" type="input">
        <parameter>problem</parameter>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage that answers the question.</instruction>
        <input>1</input>
        <output>extracted_data</output>
    </node>
    <node id="3" type="agent">
        <instruction>Perform the necessary mathematical operation based on the extracted data to compute the final answer.</instruction>
        <input>2</input>
        <output>result</output>
    </node>
    <node id="4" type="output">
        <parameter>result</parameter>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>