# Workflow ID: drop_620_0
# Benchmark: drop
# Data Indices: [2722, 3946, 2969, 1958, 1421]

<node id="1" type="input">
        <prompt>Understand the question and identify key information needed to answer it.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant details from the passage that directly relate to the question. Focus on specific numbers, names, or events mentioned.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Verify if the extracted information is sufficient to answer the question directly or if further reasoning is required.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>If multiple pieces of information are needed, combine them logically to derive the final answer.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Provide the final answer based on the combined analysis from previous steps.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>