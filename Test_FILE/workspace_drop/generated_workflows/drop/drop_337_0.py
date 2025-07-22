# Workflow ID: drop_337_0
# Benchmark: drop
# Data Indices: [68, 2239, 1860, 2642]

<node id="1" type="input">
        <prompt>Read the passage carefully and identify the key events and numerical data relevant to the question.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Extract the specific information needed to answer the question. Think step by step: First, locate the relevant section in the passage. Second, identify the exact value or event that answers the question.</prompt>
    </node>
    
    <node id="3" type="agent">
        <prompt>Verify the extracted information by cross-referencing with other parts of the passage to ensure accuracy and avoid misinterpretation.</prompt>
    </node>
    
    <node id="4" type="agent">
        <prompt>Check if the information directly answers the question. If not, determine what additional reasoning is required based on the context.</prompt>
    </node>
    
    <node id="5" type="output">
        <prompt>Provide the final answer based on the verified and logically connected information from previous steps.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>