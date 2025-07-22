# Workflow ID: drop_105_0
# Benchmark: drop
# Data Indices: [1643, 55, 939, 3086, 1149]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    <node id="2" type="process">
        <description>Parse question and extract key terms</description>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="process">
        <description>Identify relevant data in passage for the question</description>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="process">
        <description>Perform necessary calculations or logical deductions</description>
        <depends_on>3</depends_on>
    </node>
    <node id="5" type="output">
        <description>Return final answer based on processed result</description>
        <depends_on>4</depends_on>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>