# Workflow ID: hotpotqa_419_0
# Benchmark: hotpotqa
# Data Indices: [938, 692, 843, 1857, 59]

<agent id="1" type="reasoning">
        <instruction>Think step by step to identify the key entities and relationships in the problem. Focus on the main subject and its connections to other elements.</instruction>
        <input>problem</input>
        <output>structured_entities</output>
    </agent>
    <agent id="2" type="retrieval">
        <instruction>Based on the structured entities, retrieve relevant context that directly answers the question. Prioritize information with clear temporal or categorical links.</instruction>
        <input>structured_entities</input>
        <output>relevant_context</output>
    </agent>
    <agent id="3" type="verification">
        <instruction>Verify that the retrieved context contains a definitive answer. If not, flag for further analysis or indicate uncertainty.</instruction>
        <input>relevant_context</input>
        <output>verified_answer</output>
    </agent>
    <agent id="4" type="ensemble">
        <instruction>Combine the outputs from all agents into a coherent final response. Ensure clarity and correctness based on the verified answer.</instruction>
        <input>verified_answer</input>
        <output>final_output</output>
    </agent>