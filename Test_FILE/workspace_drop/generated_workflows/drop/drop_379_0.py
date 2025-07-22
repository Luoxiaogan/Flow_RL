# Workflow ID: drop_379_0
# Benchmark: drop
# Data Indices: [1762, 376, 2924, 294, 1141]

<node id="1" type="input">
        <prompt>Understand the question and identify key information needed to solve it.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant data from the passage that directly answers the question. Focus only on what is necessary for the solution.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Perform calculations or logical reasoning based on the extracted data to derive the answer.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Verify the result by cross-checking with the passage to ensure accuracy.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer in a clear, concise format.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>