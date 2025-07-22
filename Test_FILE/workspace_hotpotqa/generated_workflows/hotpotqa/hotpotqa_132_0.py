# Workflow ID: hotpotqa_132_0
# Benchmark: hotpotqa
# Data Indices: [2488, 409, 2814, 3957]

<operator id="0">
        <instruction>Identify the key entities and relationships in the input context that are relevant to answering the question.</instruction>
        <input>problem</input>
        <output>filtered_context</output>
    </operator>
    <operator id="1">
        <instruction>Extract all temporal references (years, dates) from the filtered context and map them to the relevant entities or events.</instruction>
        <input>filtered_context</input>
        <output>temporal_data</output>
    </operator>
    <operator id="2">
        <instruction>Compare the temporal data to determine which entity or event occurred first based on the year or date values.</instruction>
        <input>temporal_data</input>
        <output>earlier_event</output>
    </operator>
    <operator id="3">
        <instruction>Verify the earlier event by cross-referencing with the original context to ensure accuracy and relevance to the question.</instruction>
        <input>earlier_event, filtered_context</input>
        <output>verified_answer</output>
    </operator>
    <operator id="4">
        <instruction>Format the verified answer into a concise and clear response suitable for direct output.</instruction>
        <input>verified_answer</input>
        <output>final_output</output>
    </operator>