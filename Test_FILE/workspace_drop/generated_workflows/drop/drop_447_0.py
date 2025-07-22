# Workflow ID: drop_447_0
# Benchmark: drop
# Data Indices: [1911, 2417, 2979, 2148, 2008]

<node id="1" type="input">
        <prompt>Understand the question and identify key elements needed to solve it.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from the passage that directly answers the question. Focus on specific numbers, names, or events mentioned.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Process the extracted data—compare values, calculate differences, or identify patterns as required by the question.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Verify the result by cross-checking with other parts of the passage to ensure accuracy and avoid misinterpretation.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer based on the processed and verified information.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>