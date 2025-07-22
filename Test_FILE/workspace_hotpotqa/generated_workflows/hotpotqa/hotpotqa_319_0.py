# Workflow ID: hotpotqa_319_0
# Benchmark: hotpotqa
# Data Indices: [401, 721, 2439, 2973]

<agent id="1">
        <instruction>Identify the key entities mentioned in the context that relate to the question.</instruction>
        <input>problem</input>
        <output>entity_candidates</output>
    </agent>
    
    <agent id="2">
        <instruction>Filter candidates to find the one directly answering the question based on contextual relevance and specificity.</instruction>
        <input>entity_candidates</input>
        <output>filtered_answer</output>
    </agent>
    
    <agent id="3">
        <instruction>Validate the filtered answer by cross-referencing with known facts or logical consistency within the context.</instruction>
        <input>filtered_answer</input>
        <output>validated_answer</output>
    </agent>
    
    <agent id="4">
        <instruction>Ensure the final output is a concise, unambiguous response matching the exact format required by the question.</instruction>
        <input>validated_answer</input>
        <output>final_output</output>
    </agent>
    
    <connect from="1" to="2"/>
    <connect from="2" to="3"/>
    <connect from="3" to="4"/>