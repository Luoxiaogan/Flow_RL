# Workflow ID: drop_100_0
# Benchmark: drop
# Data Indices: [1089, 1021, 1734, 1935]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key question and relevant passage segment.</instruction>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="agent">
        <instruction>Extract numerical or categorical data related to the question from the passage.</instruction>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="agent">
        <instruction>Apply logical reasoning or arithmetic to derive the answer.</instruction>
        <depends_on>3</depends_on>
    </node>
    <node id="5" type="output">
        <description>Return the final answer based on processed information.</description>
        <depends_on>4</depends_on>
    </node>