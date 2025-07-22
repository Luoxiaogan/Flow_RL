# Workflow ID: hotpotqa_136_0
# Benchmark: hotpotqa
# Data Indices: [500, 2523, 116, 1793]

<node id="start" type="input"/>
    <node id="agent1" type="agent">
        <instruction>Think step by step to identify the key information needed to solve the problem.</instruction>
    </node>
    <node id="agent2" type="agent">
        <instruction>Extract relevant facts from the context that directly answer the question.</instruction>
    </node>
    <node id="agent3" type="agent">
        <instruction>Verify the extracted information against the question's requirements.</instruction>
    </node>
    <node id="agent4" type="agent">
        <instruction>Formulate a concise and accurate response based on verified facts.</instruction>
    </node>
    <node id="end" type="output"/>
    
    <edge from="start" to="agent1"/>
    <edge from="agent1" to="agent2"/>
    <edge from="agent2" to="agent3"/>
    <edge from="agent3" to="agent4"/>
    <edge from="agent4" to="end"/>