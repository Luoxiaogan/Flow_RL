# Workflow ID: drop_540_0
# Benchmark: drop
# Data Indices: [866, 994, 822, 3358]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    <node id="2" type="process">
        <description>Parse and extract key numerical data from passage</description>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="process">
        <description>Apply mathematical operations based on question requirements</description>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="validate">
        <description>Verify correctness of computed result against logical constraints</description>
        <depends_on>3</depends_on>
    </node>
    <node id="5" type="output">
        <description>Return final answer</description>
        <depends_on>4</depends_on>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>