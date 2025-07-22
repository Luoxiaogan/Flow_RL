# Workflow ID: drop_361_0
# Benchmark: drop
# Data Indices: [512, 1222, 2534, 3835]

<node id="1" type="input">
        <prompt>Understand the question and identify key information needed to solve it.</prompt>
    </node>
    
    <node id="2" type="process">
        <prompt>Extract relevant data from the passage that directly answers the question.</prompt>
    </node>
    
    <node id="3" type="process">
        <prompt>Perform necessary calculations or logical reasoning using the extracted data.</prompt>
    </node>
    
    <node id="4" type="validate">
        <prompt>Verify the calculation or logic is correct and aligns with the question.</prompt>
    </node>
    
    <node id="5" type="output">
        <prompt>Provide the final answer in the required format.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>