# Workflow ID: hotpotqa_421_0
# Benchmark: hotpotqa
# Data Indices: [9, 3629, 3787, 215, 2100]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from context related to the key entities.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Identify the category or classification that connects the entities.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Verify the connection using logical reasoning and cross-reference with context.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Provide the final answer based on verified connections.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>