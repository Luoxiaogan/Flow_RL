# Workflow ID: drop_715_0
# Benchmark: drop
# Data Indices: [3576, 1529, 3019, 425, 749]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    <node id="2" type="analyze">
        <description>Parse question and identify key data points</description>
    </node>
    <node id="3" type="extract">
        <description>Extract relevant numerical or categorical values from passage</description>
    </node>
    <node id="4" type="compute">
        <description>Perform arithmetic or logical operations based on extracted data</description>
    </node>
    <node id="5" type="validate">
        <description>Verify that the computed answer matches the question's requirements</description>
    </node>
    <node id="6" type="output">
        <description>Return final answer</description>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>