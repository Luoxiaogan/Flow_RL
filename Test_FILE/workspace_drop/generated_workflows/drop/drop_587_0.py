# Workflow ID: drop_587_0
# Benchmark: drop
# Data Indices: [1671, 2436, 1525, 3505]

<node id="1" type="input">
        <prompt>Read the problem carefully and identify the key numerical data points relevant to the question.</prompt>
    </node>
    <node id="2" type="process">
        <prompt>Extract all instances where a specific event (e.g., touchdown, win, percentage change) is mentioned in the passage. Focus only on those directly related to the question.</prompt>
    </node>
    <node id="3" type="process">
        <prompt>For each extracted instance, determine whether it contributes to the final answer by checking if it meets the criteria of the question (e.g., "how many", "what percentage").</prompt>
    </node>
    <node id="4" type="output">
        <prompt>Aggregate all valid contributions from step 3 into a single numeric or textual answer based on the question's requirements.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>