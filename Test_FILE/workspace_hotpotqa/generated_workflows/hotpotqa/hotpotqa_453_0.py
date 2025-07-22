# Workflow ID: hotpotqa_453_0
# Benchmark: hotpotqa
# Data Indices: [1338, 1797, 436, 2408]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from context related to the key entities.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Verify consistency between extracted information and the question's requirements.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Apply logical reasoning to derive the final answer based on verified data.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer in a clear and concise format.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>