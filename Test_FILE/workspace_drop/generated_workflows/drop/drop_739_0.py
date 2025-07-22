# Workflow ID: drop_739_0
# Benchmark: drop
# Data Indices: [3344, 42, 2575, 1024]

<node id="1" type="input">
        <prompt>Understand the question and identify key information needed to solve it.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant details from the passage that directly relate to the question. Focus only on data points that can help compute or determine the answer.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Perform necessary calculations or comparisons based on the extracted data. If the question involves a sequence of events, ensure the order is respected.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Verify that the computed result aligns with the context of the passage and matches the question's requirements exactly.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer in a clear and concise format as required by the question.</prompt>
    </node>

    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>