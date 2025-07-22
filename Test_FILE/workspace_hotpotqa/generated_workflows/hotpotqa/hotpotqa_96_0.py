# Workflow ID: hotpotqa_96_0
# Benchmark: hotpotqa
# Data Indices: [1755, 209, 972, 1523, 3177]

<operator id="1">
        <instruction>Identify the key entities and relationships in the context that directly answer the question.</instruction>
        <input>context</input>
        <output>entity_candidates</output>
    </operator>
    
    <operator id="2">
        <instruction>Filter candidates to those relevant to the specific question being asked.</instruction>
        <input>entity_candidates</input>
        <output>filtered_entities</output>
    </operator>
    
    <operator id="3">
        <instruction>Verify the filtered entity against known facts or cross-reference with other context elements for consistency.</instruction>
        <input>filtered_entities</input>
        <output>verified_entity</output>
    </operator>
    
    <operator id="4">
        <instruction>Generate a concise, direct answer based on the verified entity.</instruction>
        <input>verified_entity</input>
        <output>final_answer</output>
    </operator>
    
    <operator id="5">
        <instruction>Check if the final answer satisfies the original question's requirements without ambiguity.</instruction>
        <input>final_answer</input>
        <output>is_valid</output>
    </operator>
    
    <connect from="1" to="2"/>
    <connect from="2" to="3"/>
    <connect from="3" to="4"/>
    <connect from="4" to="5"/>