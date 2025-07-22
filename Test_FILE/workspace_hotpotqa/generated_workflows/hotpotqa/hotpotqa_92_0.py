# Workflow ID: hotpotqa_92_0
# Benchmark: hotpotqa
# Data Indices: [1315, 10, 71, 1121, 2106]

<node id="1" type="input">
        <prompt>Understand the core question and identify key entities mentioned.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant historical context from provided materials, focusing on treaties and monarchs.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Identify the last of the Numbered Treaties and the reigning monarch at that time.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Determine the year the monarch died who signed the final treaty.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the year the king died who signed the last Numbered Treaty.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>