# Workflow ID: drop_73_0
# Benchmark: drop
# Data Indices: [2811, 3716, 3563, 3601]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    <node id="2" type="process">
        <description>Parse and extract relevant numerical data from the passage</description>
    </node>
    <node id="3" type="process">
        <description>Identify specific values based on question requirements (e.g., field goals in a half, touchdowns between 5-20 yards)</description>
    </node>
    <node id="4" type="logic">
        <description>Apply logical filtering: e.g., count field goals in second half, filter touchdowns by yard range</description>
    </node>
    <node id="5" type="compute">
        <description>Perform arithmetic or comparison operations to derive answer</description>
    </node>
    <node id="6" type="output">
        <description>Return final numeric result</description>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>