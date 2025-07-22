# Workflow ID: drop_84_0
# Benchmark: drop
# Data Indices: [1611, 2933, 1201, 2500, 3668]

<node id="1" type="input">
        <prompt>Understand the question and identify key elements from the passage.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information related to the question. Focus on specific details like names, scores, or events mentioned in the passage.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Process the extracted data to determine the correct answer by comparing or calculating as needed.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Verify the result by cross-checking with the passage for accuracy and consistency.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer based on the verified result.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>