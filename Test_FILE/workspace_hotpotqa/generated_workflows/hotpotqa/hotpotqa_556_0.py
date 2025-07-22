# Workflow ID: hotpotqa_556_0
# Benchmark: hotpotqa
# Data Indices: [2531, 244, 3184, 56, 2653]

<operator id="1">
        <instruction>Identify the key entities and their relationships in the problem context.</instruction>
        <input>problem</input>
        <output>entity_list</output>
    </operator>
    
    <operator id="2">
        <instruction>Extract temporal or categorical data relevant to the question from the entity list.</instruction>
        <input>entity_list</input>
        <output>temporal_data</output>
    </operator>
    
    <operator id="3">
        <instruction>Compare the extracted data to determine which entity satisfies the condition in the question.</instruction>
        <input>temporal_data</input>
        <output>comparison_result</output>
    </operator>
    
    <operator id="4">
        <instruction>Validate the comparison result against known facts or constraints in the context.</instruction>
        <input>comparison_result</input>
        <output>validated_answer</output>
    </operator>
    
    <operator id="5">
        <instruction>Format the validated answer into a clear, concise response.</instruction>
        <input>validated_answer</input>
        <output>final_output</output>
    </operator>
    
    <operator id="6">
        <instruction>Check if the final output meets all criteria: correctness, clarity, and completeness.</instruction>
        <input>final_output</input>
        <output>quality_assurance</output>
    </operator>
    
    <operator id="7">
        <instruction>Return the final verified answer.</instruction>
        <input>quality_assurance</input>
        <output>answer</output>
    </operator>