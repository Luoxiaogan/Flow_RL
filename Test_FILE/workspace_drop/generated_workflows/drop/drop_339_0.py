# Workflow ID: drop_339_0
# Benchmark: drop
# Data Indices: [1681, 1224, 25, 2897]

<node id="1" type="input">
        <parameter>problem</parameter>
    </node>
    <node id="2" type="process">
        <operation>extract_numerical_data</operation>
        <input>1</input>
    </node>
    <node id="3" type="process">
        <operation>calculate_difference</operation>
        <input>2</input>
    </node>
    <node id="4" type="output">
        <parameter>result</parameter>
        <input>3</input>
    </node>