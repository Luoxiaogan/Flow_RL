# Workflow ID: hotpotqa_46_0
# Benchmark: hotpotqa
# Data Indices: [2740, 1244, 172, 151]

<agent id="1" type="extract">
        <instruction>Extract the key entities and relationships from the input context relevant to the question.</instruction>
    </agent>
    <agent id="2" type="reason">
        <instruction>Reason step by step: Identify the film in question, determine who produced it, and then identify the most notable work of that producer.</instruction>
    </agent>
    <agent id="3" type="validate">
        <instruction>Validate that the producer's most notable coproduction matches the information in the context. Ensure no conflicting or missing links exist.</instruction>
    </agent>
    <agent id="4" type="combine">
        <instruction>Combine the validated result from agent 2 with the output from agent 3 to form a final answer.</instruction>
    </agent>
    <edge from="1" to="2" />
    <edge from="2" to="3" />
    <edge from="3" to="4" />