# Workflow ID: drop_569_0
# Benchmark: drop
# Data Indices: [2284, 2942, 2121, 2827, 2664]

<node id="1" type="input">
        <parameter>problem</parameter>
    </node>
    <node id="2" type="process">
        <operation>extract_percentage_data</operation>
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