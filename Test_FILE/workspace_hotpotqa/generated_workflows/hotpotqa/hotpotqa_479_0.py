# Workflow ID: hotpotqa_479_0
# Benchmark: hotpotqa
# Data Indices: [2435, 447, 2417, 3542, 3776]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from context related to the key entities.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Identify the connection between the inherited castle and the nearest city.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Determine the city nearest to the castle based on geographical or contextual clues.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the name of the nearest city to the inherited castle.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>