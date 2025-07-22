# Workflow ID: drop_889_0
# Benchmark: drop
# Data Indices: [7, 119, 1557, 3397]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    <node id="2" type="process">
        <description>Parse question to identify required information</description>
        <dependencies>[1]</dependencies>
    </node>
    <node id="3" type="process">
        <description>Extract relevant data from passage based on question</description>
        <dependencies>[2]</dependencies>
    </node>
    <node id="4" type="reason">
        <description>Apply logical reasoning to compare or calculate the answer</description>
        <dependencies>[3]</dependencies>
    </node>
    <node id="5" type="output">
        <description>Generate final answer based on computed result</description>
        <dependencies>[4]</dependencies>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>