# Workflow ID: hotpotqa_123_0
# Benchmark: hotpotqa
# Data Indices: [3266, 109, 1050, 1330, 1057]

<node id="1" type="input">
        <prompt>Process the given problem context and identify key entities, relationships, and constraints.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Extract relevant information from the context that directly answers the question. Focus on specific names, dates, or titles mentioned in relation to the query.</prompt>
    </node>
    
    <node id="3" type="agent">
        <prompt>Verify if the extracted information matches the exact requirement of the question. If not, search for indirect connections or alternative references in the context.</prompt>
    </node>
    
    <node id="4" type="agent">
        <prompt>Construct a precise answer based on validated evidence. Avoid adding unsupported details or assumptions.</prompt>
    </node>
    
    <node id="5" type="output">
        <prompt>Return the final answer as a concise, clear response to the original question.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>