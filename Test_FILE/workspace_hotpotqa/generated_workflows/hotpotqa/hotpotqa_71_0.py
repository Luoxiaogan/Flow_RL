# Workflow ID: hotpotqa_71_0
# Benchmark: hotpotqa
# Data Indices: [2603, 1515, 2458, 2088, 1804]

<start/>
    <agent id="1" type="reasoning">
        <instruction>Think step by step to identify the correct answer based on the provided context.</instruction>
    </agent>
    <agent id="2" type="retrieval">
        <instruction>Extract relevant information from the context that directly answers the question.</instruction>
    </agent>
    <agent id="3" type="comparison">
        <instruction>Compare the extracted information to determine the correct answer.</instruction>
    </agent>
    <agent id="4" type="verification">
        <instruction>Verify the consistency of the answer with all available context clues.</instruction>
    </agent>
    <agent id="5" type="synthesis">
        <instruction>Combine insights from previous agents to produce a final, accurate response.</instruction>
    </agent>
    <end/>