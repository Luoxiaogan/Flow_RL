# Workflow ID: drop_862_0
# Benchmark: drop
# Data Indices: [3323, 339, 519, 1120, 1818]

<node id="1" type="input">
        <prompt>Read the passage carefully and identify the key numerical data points relevant to the question.</prompt>
    </node>
    
    <node id="2" type="process">
        <prompt>Extract the year of the First Utrecht Civil War's end and the year of the Second Utrecht Civil War's start.</prompt>
    </node>
    
    <node id="3" type="compute">
        <prompt>Calculate the difference between the two years to determine the number of years between the wars.</prompt>
    </node>
    
    <node id="4" type="output">
        <prompt>Return the calculated number of years as the final answer.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>