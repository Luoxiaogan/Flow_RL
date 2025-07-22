# Workflow ID: drop_212_0
# Benchmark: drop
# Data Indices: [1583, 52, 3798, 1366]

<node id="1" type="input">
        <prompt>Understand the problem statement and identify the key information needed to solve it.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Extract relevant data from the passage that directly answers the question. Think step by step: first identify what is being asked, then locate the corresponding numbers or facts in the text.</prompt>
    </node>
    
    <node id="3" type="agent">
        <prompt>Perform necessary calculations using the extracted data. For example, if the question asks for a percentage, ensure you use the correct formula (e.g., 100% - given percentage).</prompt>
    </node>
    
    <node id="4" type="agent">
        <prompt>Verify the calculation logic and check for consistency with the context of the problem. Ensure no data was misinterpreted or omitted.</prompt>
    </node>
    
    <node id="5" type="output">
        <prompt>Return the final answer as a concise, accurate result based on the verified calculation.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>