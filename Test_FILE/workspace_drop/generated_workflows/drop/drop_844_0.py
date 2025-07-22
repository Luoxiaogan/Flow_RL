# Workflow ID: drop_844_0
# Benchmark: drop
# Data Indices: [2906, 1411, 1231, 580]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    <node id="2" type="analyze">
        <description>Break down the question and identify key data points</description>
    </node>
    <node id="3" type="extract">
        <description>Extract relevant numbers or values from passage</description>
    </node>
    <node id="4" type="compute">
        <description>Perform necessary calculations based on extracted data</description>
    </node>
    <node id="5" type="validate">
        <description>Check if the computed answer matches logical constraints</description>
    </node>
    <node id="6" type="output">
        <description>Return final answer</description>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>