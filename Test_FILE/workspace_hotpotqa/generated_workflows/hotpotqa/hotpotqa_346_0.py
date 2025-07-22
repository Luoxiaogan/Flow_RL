# Workflow ID: hotpotqa_346_0
# Benchmark: hotpotqa
# Data Indices: [2669, 1061, 959, 1176]

<agent id="1" type="reasoning">
        <instruction>Think step by step to identify the key elements in the context that relate to the question. Focus on the specific details that can lead to the correct answer.</instruction>
        <input>problem</input>
        <output>filtered_context</output>
    </agent>
    <agent id="2" type="search">
        <instruction>Extract only the relevant entities or phrases from the filtered context that directly address the question. Avoid including any unrelated information.</instruction>
        <input>filtered_context</input>
        <output>relevant_entities</output>
    </agent>
    <agent id="3" type="verification">
        <instruction>Verify whether the extracted entities match the required answer format and ensure they are unambiguous. If multiple candidates exist, prioritize based on specificity and direct relevance.</instruction>
        <input>relevant_entities</input>
        <output>verified_answer</output>
    </agent>
    <agent id="4" type="ensemble">
        <instruction>Combine outputs from previous agents into a single coherent response. Ensure the final output is concise and directly answers the question without extra explanation.</instruction>
        <input>verified_answer</input>
        <output>final_output</output>
    </agent>