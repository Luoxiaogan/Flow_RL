# Workflow ID: drop_239_0
# Benchmark: drop
# Data Indices: [3750, 3435, 1933, 3878]

<node id="1" type="input">
        <prompt>Understand the question and extract key information.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Identify the relevant data in the passage that directly answers the question. Think step by step: what specific detail is being asked? What part of the passage contains that detail?</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Verify that the extracted information matches the question exactly. If not, re-examine the passage for any indirect clues or numerical references that might support the answer.</prompt>
    </node>
    <node id="4" type="operator">
        <prompt>Use a loop to iterate through possible values or comparisons if multiple options exist (e.g., comparing scores or point differences).</prompt>
    </node>
    <node id="5" type="operator">
        <prompt>Apply arithmetic logic (e.g., subtraction) to compute the difference between two values when required.</prompt>
    </node>
    <node id="6" type="output">
        <prompt>Return the final answer based on verified and computed data.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>