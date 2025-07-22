# Workflow ID: hotpotqa_257_0
# Benchmark: hotpotqa
# Data Indices: [3749, 1500, 2539, 1947, 660]

<operator id="1">
        <instruction>Identify the key entities and relationships in the problem context to determine the correct answer.</instruction>
        <input>problem</input>
        <output>entity_list</output>
    </operator>
    <operator id="2">
        <instruction>Extract specific facts relevant to the question from the entity list, focusing on direct matches or logical connections.</instruction>
        <input>entity_list</input>
        <output>relevant_facts</output>
    </operator>
    <operator id="3">
        <instruction>Validate each relevant fact against the question to ensure accuracy and eliminate ambiguity.</instruction>
        <input>relevant_facts</input>
        <output>validated_evidence</output>
    </operator>
    <operator id="4">
        <instruction>Use logical reasoning to derive the final answer based on the validated evidence.</instruction>
        <input>validated_evidence</input>
        <output>final_answer</output>
    </operator>
    <operator id="5">
        <instruction>Double-check that the final answer directly addresses the question without unnecessary elaboration.</instruction>
        <input>final_answer</input>
        <output>conclusion</output>
    </operator>