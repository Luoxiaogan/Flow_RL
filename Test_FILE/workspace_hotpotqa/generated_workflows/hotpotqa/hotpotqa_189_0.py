# Workflow ID: hotpotqa_189_0
# Benchmark: hotpotqa
# Data Indices: [325, 996, 2634, 3239, 702]

<operator id="1">
        <instruction>Identify the key entities and relationships in the problem context to determine what needs to be extracted.</instruction>
        <input>problem</input>
        <output>entity_list</output>
    </operator>
    
    <operator id="2">
        <instruction>Extract specific facts related to the question from the entity list, focusing on the connection between the song and the campaign.</instruction>
        <input>entity_list</input>
        <output>relevant_facts</output>
    </operator>
    
    <operator id="3">
        <instruction>Verify that the extracted facts directly answer the question by checking for explicit mentions of the song's use in a campaign tied to public education revenue in New York.</instruction>
        <input>relevant_facts</input>
        <output>verification_result</output>
    </operator>
    
    <operator id="4">
        <instruction>If verification passes, return the song name as the final answer. If not, indicate no valid answer found.</instruction>
        <input>verification_result</input>
        <output>final_answer</output>
    </operator>