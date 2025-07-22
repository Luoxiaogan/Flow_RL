# Workflow ID: drop_356_0
# Benchmark: drop
# Data Indices: [2261, 3826, 2883, 805]

<node id="1" type="input">
        <prompt>Extract all field goal distances from the passage.</prompt>
        <output>list of field goal distances</output>
    </node>
    
    <node id="2" type="operator">
        <prompt>Identify the maximum value from the list of field goal distances.</prompt>
        <output>longest field goal distance</output>
    </node>
    
    <node id="3" type="output">
        <prompt>Return the longest field goal distance as the final answer.</prompt>
        <input>longest field goal distance</input>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>