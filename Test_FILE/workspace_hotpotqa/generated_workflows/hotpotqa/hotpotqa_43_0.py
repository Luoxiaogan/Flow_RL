# Workflow ID: hotpotqa_43_0
# Benchmark: hotpotqa
# Data Indices: [2269, 1765, 361, 1657, 2340]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from the context related to the key entities.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Verify that the extracted information directly answers the question.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Ensure no irrelevant details are included in the final answer.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the correct answer based on verified information.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>