# Workflow ID: hotpotqa_57_0
# Benchmark: hotpotqa
# Data Indices: [1256, 1159, 1219, 2898, 763]

<operator id="1">
        <instruction>Identify the key entities and relationships in the problem context.</instruction>
        <input>problem</input>
        <output>entity_list, relationship_map</output>
    </operator>
    
    <operator id="2">
        <instruction>Extract temporal ranges and relevant titles from the peerage context.</instruction>
        <input>relationship_map</input>
        <output>time_range_matches</output>
    </operator>
    
    <operator id="3">
        <instruction>Filter for lawyers/judges who served during the specified period (1801–1898).</instruction>
        <input>time_range_matches</input>
        <output>lawyer_judge_candidates</output>
    </operator>
    
    <operator id="4">
        <instruction>Verify which candidate was elevated to the Peerage of the United Kingdom during the given timeframe.</instruction>
        <input>lawyer_judge_candidates</input>
        <output>verified_peer</output>
    </operator>
    
    <operator id="5">
        <instruction>Confirm the title and service period of the verified peer to ensure alignment with the question's constraints.</instruction>
        <input>verified_peer</input>
        <output>final_answer</output>
    </operator>
    
    <operator id="6">
        <instruction>Validate that the final answer matches both the time frame and role (prominent lawyer judge) as required by the question.</instruction>
        <input>final_answer</input>
        <output>is_valid</output>
    </operator>
    
    <operator id="7">
        <instruction>Return the validated answer if valid; otherwise, raise an error indicating missing information.</instruction>
        <input>is_valid, final_answer</input>
        <output>return_value</output>
    </operator>