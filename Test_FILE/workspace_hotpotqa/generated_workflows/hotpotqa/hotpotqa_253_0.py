# Workflow ID: hotpotqa_253_0
# Benchmark: hotpotqa
# Data Indices: [2938, 2218, 3577, 2474, 2224]

<start/>
    <node id="1" type="agent">
        <instruction>Identify the key entity in the question and locate its relevant context.</instruction>
    </node>
    <node id="2" type="agent">
        <instruction>Extract the specific detail required to answer the question from the context.</instruction>
    </node>
    <node id="3" type="agent">
        <instruction>Verify that the extracted detail directly answers the question without ambiguity.</instruction>
    </node>
    <node id="4" type="agent">
        <instruction>Ensure the final answer is concise, accurate, and matches the format expected by the question.</instruction>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <end/>