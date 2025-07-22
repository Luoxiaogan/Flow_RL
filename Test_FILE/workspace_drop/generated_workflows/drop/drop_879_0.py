# Workflow ID: drop_879_0
# Benchmark: drop
# Data Indices: [419, 3752, 637, 394, 1363]

<node id="1" type="input">
        <prompt>Read the passage carefully and identify all touchdown passes mentioned.</prompt>
    </node>
    
    <node id="2" type="process">
        <prompt>Extract the yardage of each touchdown pass from the passage.</prompt>
    </node>
    
    <node id="3" type="process">
        <prompt>Sort the touchdown passes by yardage in ascending order to find the shortest.</prompt>
    </node>
    
    <node id="4" type="output">
        <prompt>Return the yardage of the shortest touchdown pass identified.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>