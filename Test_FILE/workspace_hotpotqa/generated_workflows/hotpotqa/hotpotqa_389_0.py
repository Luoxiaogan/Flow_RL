# Workflow ID: hotpotqa_389_0
# Benchmark: hotpotqa
# Data Indices: [416, 580, 365, 3221, 2703]

<operator id="0">
        <instruction>Identify the key entities and relationships in the input context to determine the correct answer.</instruction>
        <input>problem</input>
        <output>entity_relations</output>
    </operator>
    <operator id="1">
        <instruction>Extract only the relevant facts that directly address the question from the entity relations.</instruction>
        <input>entity_relations</input>
        <output>relevant_facts</output>
    </operator>
    <operator id="2">
        <instruction>Verify if the extracted facts contain a direct match or sufficient evidence to answer the question.</instruction>
        <input>relevant_facts</input>
        <output>verified_answer</output>
    </operator>
    <operator id="3">
        <instruction>If no direct answer is found, infer based on logical connections between entities and temporal context.</instruction>
        <input>relevant_facts</input>
        <output>inferred_answer</output>
    </operator>
    <operator id="4">
        <instruction>Combine verified and inferred answers to form a single, coherent response.</instruction>
        <input>verified_answer, inferred_answer</input>
        <output>final_answer</output>
    </operator>
    <operator id="5">
        <instruction>Validate final answer against all provided context to ensure accuracy and completeness.</instruction>
        <input>final_answer, problem</input>
        <output>validated_final_answer</output>
    </operator>