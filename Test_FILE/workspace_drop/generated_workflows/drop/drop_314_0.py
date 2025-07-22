# Workflow ID: drop_314_0
# Benchmark: drop
# Data Indices: [2036, 204, 3658, 2313, 3242]

<node id="1" type="input">
        <prompt>Understand the question and identify key data points needed to solve it.</prompt>
    </node>
    
    <node id="2" type="process">
        <prompt>Extract relevant numerical values or percentages from the passage based on the question.</prompt>
    </node>
    
    <node id="3" type="process">
        <prompt>Perform arithmetic operations (e.g., subtraction, percentage change) to compute the answer.</prompt>
    </node>
    
    <node id="4" type="output">
        <prompt>Return the final computed value as the answer to the question.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>