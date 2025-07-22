# Workflow ID: drop_230_0
# Benchmark: drop
# Data Indices: [3008, 1271, 2141, 2042, 106]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="process">
        <operation>extract_relevant_data</operation>
        <dependencies>1</dependencies>
    </node>
    <node id="3" type="process">
        <operation>calculate_percentage</operation>
        <dependencies>2</dependencies>
    </node>
    <node id="4" type="output">
        <operation>format_result</operation>
        <dependencies>3</dependencies>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>