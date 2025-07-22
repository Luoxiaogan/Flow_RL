# Workflow ID: drop_456_0
# Benchmark: drop
# Data Indices: [2458, 1423, 312, 3999]

<node id="1" type="input">
        <prompt>Extract the key numerical values from the passage relevant to the question.</prompt>
    </node>
    
    <node id="2" type="process">
        <prompt>Identify the specific values needed to compute the difference (e.g., yards of field goal and interception run).</prompt>
    </node>
    
    <node id="3" type="calculate">
        <prompt>Compute the difference between the two identified values using subtraction.</prompt>
    </node>
    
    <node id="4" type="output">
        <prompt>Return the computed difference as the final answer.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>