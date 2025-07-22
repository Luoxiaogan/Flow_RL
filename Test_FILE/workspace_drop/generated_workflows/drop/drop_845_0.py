# Workflow ID: drop_845_0
# Benchmark: drop
# Data Indices: [3287, 3702, 2865, 568]

<node id="1" type="input">
        <prompt>Extract relevant numerical data from the passage related to field goals.</prompt>
    </node>
    
    <node id="2" type="process">
        <prompt>Identify the longest field goal distance and the specific kicker associated with it.</prompt>
    </node>
    
    <node id="3" type="process">
        <prompt>Identify the field goal distance of Alex Henery and note the value.</prompt>
    </node>
    
    <node id="4" type="compute">
        <prompt>Calculate the difference between the longest field goal and Alex Henery's field goal.</prompt>
    </node>
    
    <node id="5" type="output">
        <prompt>Return the calculated difference in yards.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="1" to="3"/>
    <edge from="2" to="4"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>