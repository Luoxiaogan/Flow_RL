# Workflow ID: hotpotqa_323_0
# Benchmark: hotpotqa
# Data Indices: [886, 1505, 2349, 1092]

<node id="start" type="input"/>
    <node id="agent1" type="agent">
        <instruction>Think step by step to identify the core subject and context of the problem. Break down the question into its key components and determine what specific information is being asked.</instruction>
    </node>
    <node id="agent2" type="agent">
        <instruction>Based on the output from agent1, locate and extract the relevant factual information from the provided context that directly answers the question. Ensure precision and avoid unnecessary details.</instruction>
    </node>
    <node id="agent3" type="agent">
        <instruction>Verify the extracted information from agent2 against the original question to ensure it fully addresses what was asked. If incomplete, refine the answer using additional context or clarify ambiguity.</instruction>
    </node>
    <node id="agent4" type="agent">
        <instruction>Rephrase the verified answer clearly and concisely, ensuring it matches the format required by the question (e.g., a name, term, or phrase). Avoid markdown formatting in the final output.</instruction>
    </node>
    <node id="end" type="output"/>
    <edge from="start" to="agent1"/>
    <edge from="agent1" to="agent2"/>
    <edge from="agent2" to="agent3"/>
    <edge from="agent3" to="agent4"/>
    <edge from="agent4" to="end"/>