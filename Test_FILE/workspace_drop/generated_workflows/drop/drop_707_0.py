# Workflow ID: drop_707_0
# Benchmark: drop
# Data Indices: [3250, 1605, 3166, 3195]

<node id="1" type="input">
        <prompt>Understand the question and identify key information needed to solve it.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant data from the passage that directly answers the question. Focus on chronological order, numerical values, or specific events mentioned.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Process the extracted data: compare timelines, calculate differences, or identify the correct entity based on context.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Verify the result by cross-checking with the passage to ensure accuracy and avoid misinterpretation.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer in a clear and concise format, matching the question's requirements.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>