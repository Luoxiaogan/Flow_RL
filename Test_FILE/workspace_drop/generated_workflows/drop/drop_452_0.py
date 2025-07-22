# Workflow ID: drop_452_0
# Benchmark: drop
# Data Indices: [909, 1014, 1953, 2294]

<node id="1" type="input">
        <prompt>Extract the relevant information from the passage related to the question.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Identify all field goals mentioned in the passage and their distances.</prompt>
    </node>
    
    <node id="3" type="agent">
        <prompt>Determine which field goals were kicked by Bironas based on the passage.</prompt>
    </node>
    
    <node id="4" type="agent">
        <prompt>Count how many field goals Bironas successfully made.</prompt>
    </node>
    
    <node id="5" type="output">
        <prompt>Return the number of field goals Bironas kicked.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>