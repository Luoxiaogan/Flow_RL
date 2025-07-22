# Workflow ID: drop_229_0
# Benchmark: drop
# Data Indices: [589, 2909, 2765, 2033]

<node id="1" type="input">
        <prompt>Understand the question and identify the key data needed to solve it.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Extract relevant numerical values from the passage related to the question. Think step by step: locate the exact figures for each entity mentioned in the question.</prompt>
    </node>
    
    <node id="3" type="agent">
        <prompt>Perform the required arithmetic operation (e.g., subtraction, comparison) using the extracted values. Ensure accuracy by double-checking the numbers and the operation.</prompt>
    </node>
    
    <node id="4" type="output">
        <prompt>Return the final computed result as the answer to the question.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>