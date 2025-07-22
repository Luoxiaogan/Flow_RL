# Workflow ID: drop_330_0
# Benchmark: drop
# Data Indices: [1903, 1320, 802, 70, 1264]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities or values to extract.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from the passage related to the question. Focus on specific details like names, numbers, or events.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Verify that all necessary data points are retrieved and match the question's requirements.</prompt>
    </node>
    <node id="4" type="operator">
        <prompt>Apply logical reasoning or arithmetic operations if needed (e.g., counting distinct people, summing values, comparing numbers).</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer based on processed information.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>