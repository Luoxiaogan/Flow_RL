# Workflow ID: hotpotqa_73_0
# Benchmark: hotpotqa
# Data Indices: [119, 3882, 1467, 1972, 2121]

<node id="1" type="input">
        <prompt>Understand the problem and extract key entities and relationships.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Identify the relevant information in the context that answers the question. Think step by step to avoid missing critical details.</prompt>
    </node>
    
    <node id="3" type="agent">
        <prompt>Compare the extracted data points (e.g., formation years, birth dates) to determine which entity came first.</prompt>
    </node>
    
    <node id="4" type="agent">
        <prompt>Verify the comparison logic with the context to ensure accuracy—check for any conflicting or ambiguous statements.</prompt>
    </node>
    
    <node id="5" type="output">
        <prompt>Provide a clear and concise final answer based on the verified comparison.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>