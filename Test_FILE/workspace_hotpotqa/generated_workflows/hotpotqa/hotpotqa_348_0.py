# Workflow ID: hotpotqa_348_0
# Benchmark: hotpotqa
# Data Indices: [1286, 729, 1580, 952]

<operator id="1">
        <instruction>Identify the key entities and their relationships in the problem context.</instruction>
        <input>problem</input>
        <output>entity_relations</output>
    </operator>
    <operator id="2">
        <instruction>Extract candidate answers by matching the question's requirements with the provided context.</instruction>
        <input>entity_relations</input>
        <output>candidate_answers</output>
    </operator>
    <operator id="3">
        <instruction>Validate each candidate answer against all relevant context clues to eliminate mismatches.</instruction>
        <input>candidate_answers</input>
        <output>validated_answers</output>
    </operator>
    <operator id="4">
        <instruction>Rank the validated answers based on specificity, relevance, and contextual support.</instruction>
        <input>validated_answers</input>
        <output>ranked_answers</output>
    </operator>
    <operator id="5">
        <instruction>Return the top-ranked answer as the final solution.</instruction>
        <input>ranked_answers</input>
        <output>final_answer</output>
    </operator>