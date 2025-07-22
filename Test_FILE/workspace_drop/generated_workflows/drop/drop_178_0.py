# Workflow ID: drop_178_0
# Benchmark: drop
# Data Indices: [1202, 3952, 3847, 3512, 2161]

<node id="1" type="input">
        <prompt>Understand the question and identify key elements needed to solve it.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from the passage that directly answers the question. Focus on specific numbers, names, or events mentioned.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Perform necessary calculations or comparisons based on the extracted data (e.g., counting touchdowns, comparing values).</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Verify that your answer matches the exact requirement of the question—no extra or missing details.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer as a concise numerical value or clear statement.</prompt>
    </node>

    <!-- Connections -->
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>