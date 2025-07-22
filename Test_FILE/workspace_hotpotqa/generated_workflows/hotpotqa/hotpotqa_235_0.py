# Workflow ID: hotpotqa_235_0
# Benchmark: hotpotqa
# Data Indices: [413, 1708, 3339, 3099]

<agent id="1">
        <instruction>Identify the key entities and relationships in the problem statement. Focus on extracting the main subject, attributes, and connections.</instruction>
        <input>problem</input>
        <output>entity_list, relationship_graph</output>
    </agent>
    
    <agent id="2">
        <instruction>Based on the extracted entities, determine which ones are directly relevant to answering the question. Filter out irrelevant or ambiguous information.</instruction>
        <input>entity_list, relationship_graph</input>
        <output>filtered_entities</output>
    </agent>
    
    <agent id="3">
        <instruction>Use the filtered entities to locate the exact answer within the context. Prioritize direct matches over inferred or indirect references.</instruction>
        <input>filtered_entities, context</input>
        <output>candidate_answer</output>
    </agent>
    
    <agent id="4">
        <instruction>Validate the candidate answer by cross-referencing with other parts of the context. Ensure consistency and eliminate contradictions.</instruction>
        <input>candidate_answer, context</input>
        <output>validated_answer</output>
    </agent>
    
    <agent id="5">
        <instruction>Format the final answer according to the required structure. If no valid answer is found, return 'None'.</instruction>
        <input>validated_answer</input>
        <output>final_output</output>
    </agent>
    
    <connection>
        <from>1</from>
        <to>2</to>
    </connection>
    
    <connection>
        <from>2</from>
        <to>3</to>
    </connection>
    
    <connection>
        <from>3</from>
        <to>4</to>
    </connection>
    
    <connection>
        <from>4</from>
        <to>5</to>
    </connection>