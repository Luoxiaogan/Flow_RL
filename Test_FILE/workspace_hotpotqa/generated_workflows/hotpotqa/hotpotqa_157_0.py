# Workflow ID: hotpotqa_157_0
# Benchmark: hotpotqa
# Data Indices: [1852, 1368, 2616, 2165, 22]

<node id="1" type="agent">
        <instruction>Think step by step to identify the key entity in the question and locate its corresponding context.</instruction>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant information from the context that directly answers the question. Focus only on the specific detail required.</instruction>
    </node>
    <node id="3" type="agent">
        <instruction>Verify the extracted answer against the original question to ensure correctness and relevance.</instruction>
    </node>
    <node id="4" type="agent">
        <instruction>Generate the final output based on the verified answer, ensuring clarity and precision.</instruction>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>