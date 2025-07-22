# Workflow ID: drop_103_0
# Benchmark: drop
# Data Indices: [910, 3405, 1466, 846]

<node id="1" type="input">
        <prompt>Understand the question and identify key elements needed to solve it.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from the passage related to the question. Focus on specific details like names, scores, or events mentioned.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Perform necessary calculations or comparisons based on the extracted data. For example, if comparing yardage or counting touchdowns, ensure accuracy in arithmetic.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Verify that the answer aligns with the question and all steps are logically consistent. Double-check for any misinterpretations of the passage.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer clearly and concisely, ensuring it directly addresses the question.</prompt>
    </node>

    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>