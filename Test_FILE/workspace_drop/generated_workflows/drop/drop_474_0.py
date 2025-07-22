# Workflow ID: drop_474_0
# Benchmark: drop
# Data Indices: [3677, 677, 1627, 413, 2158]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    <node id="2" type="process">
        <description>Parse and extract relevant data from the passage</description>
    </node>
    <node id="3" type="process">
        <description>Apply mathematical operations to compute required values</description>
    </node>
    <node id="4" type="validate">
        <description>Verify correctness of computed result</description>
    </node>
    <node id="5" type="output">
        <description>Return final answer in specified format</description>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>