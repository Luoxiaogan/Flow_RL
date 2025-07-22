# Workflow ID: hotpotqa_445_0
# Benchmark: hotpotqa
# Data Indices: [1317, 2205, 2071, 2710]

<operator id="0">
        <instruction>Identify the key entities and relationships in the input context that are relevant to the question.</instruction>
        <input>problem</input>
        <output>filtered_context</output>
    </operator>
    <operator id="1">
        <instruction>Extract candidate answers by matching the question's focus with entities in the filtered context.</instruction>
        <input>filtered_context</input>
        <output>candidate_answers</output>
    </operator>
    <operator id="2">
        <instruction>Validate each candidate answer against all provided contextual clues to eliminate false positives.</instruction>
        <input>candidate_answers</input>
        <output>validated_answers</output>
    </operator>
    <operator id="3">
        <instruction>Rank the validated answers based on relevance, specificity, and consistency with the question's intent.</instruction>
        <input>validated_answers</input>
        <output>ranked_answers</output>
    </operator>
    <operator id="4">
        <instruction>Return the top-ranked answer as the final solution.</instruction>
        <input>ranked_answers</input>
        <output>final_answer</output>
    </operator>