# Workflow ID: hotpotqa_231_0
# Benchmark: hotpotqa
# Data Indices: [3765, 2495, 2304, 124, 1930]

<node id="1" type="input">
        <prompt>Understand the question and extract key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Identify the relevant context related to the key entities from the input.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Find the specific relationship or connection between the entities in the context.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Verify if the connection leads directly to the answer by cross-referencing with known facts.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer based on verified connections.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>