# Workflow ID: hotpotqa_160_0
# Benchmark: hotpotqa
# Data Indices: [3557, 327, 1892, 2776, 913]

<operator id="0">
        <instruction>Identify the key entities and relationships in the input context that are relevant to the question.</instruction>
        <input>problem</input>
        <output>filtered_context</output>
    </operator>
    <operator id="1">
        <instruction>Extract candidate answers by matching the question's requirements with the filtered context. Think step by step to avoid missing critical details.</instruction>
        <input>filtered_context</input>
        <output>candidate_answers</output>
    </operator>
    <operator id="2">
        <instruction>Validate each candidate answer against all provided context to ensure accuracy and eliminate ambiguity.</instruction>
        <input>candidate_answers</input>
        <output>validated_answers</output>
    </operator>
    <operator id="3">
        <instruction>Rank the validated answers based on relevance, specificity, and contextual support from the input.</instruction>
        <input>validated_answers</input>
        <output>ranked_answers</output>
    </operator>
    <operator id="4">
        <instruction>Return the top-ranked answer as the final solution, ensuring it directly addresses the original question.</instruction>
        <input>ranked_answers</input>
        <output>final_answer</output>
    </operator>