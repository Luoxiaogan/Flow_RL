# Workflow ID: hotpotqa_573_0
# Benchmark: hotpotqa
# Data Indices: [3572, 222, 3446, 2788, 1154]

<node id="1" type="input">
        <prompt>Understand the problem and identify key entities mentioned.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Extract relevant information from the context that directly answers the question. Focus on specific details like names, locations, or events tied to the question.</prompt>
    </node>
    
    <node id="3" type="agent">
        <prompt>Verify the extracted information by cross-referencing with other parts of the context to ensure accuracy and avoid misinterpretation.</prompt>
    </node>
    
    <node id="4" type="agent">
        <prompt>Construct a concise answer based on the verified information, ensuring it directly addresses the question without unnecessary elaboration.</prompt>
    </node>
    
    <node id="5" type="output">
        <prompt>Return the final answer as a clear and accurate response to the question.</prompt>
    </node>

    <!-- Edges -->
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>