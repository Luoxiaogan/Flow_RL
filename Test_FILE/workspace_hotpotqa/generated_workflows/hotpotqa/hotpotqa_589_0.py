# Workflow ID: hotpotqa_589_0
# Benchmark: hotpotqa
# Data Indices: [3814, 11, 3981, 1911]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from the context related to the key entities. Focus on precise details that answer the question directly.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Verify the extracted information against the full context to ensure accuracy and avoid misinterpretation.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Structure the final answer in a clear, concise format based on verified information.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the correctly formatted answer.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>