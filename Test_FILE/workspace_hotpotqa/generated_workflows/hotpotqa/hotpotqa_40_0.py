# Workflow ID: hotpotqa_40_0
# Benchmark: hotpotqa
# Data Indices: [2428, 2170, 2744, 2196]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Extract relevant context information related to the key entities from the provided text.</prompt>
    </node>
    
    <node id="3" type="agent">
        <prompt>Verify that the extracted context contains a direct match or clear inference for the answer.</prompt>
    </node>
    
    <node id="4" type="agent">
        <prompt>Ensure the answer is unambiguous and directly supported by the context, without speculation.</prompt>
    </node>
    
    <node id="5" type="output">
        <prompt>Return the final answer based on verified context.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>