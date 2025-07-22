# Workflow ID: hotpotqa_238_0
# Benchmark: hotpotqa
# Data Indices: [3831, 1736, 1141, 21]

<operator id="0">
        <instruction>Identify the key entities and relationships in the problem context.</instruction>
        <input>problem</input>
        <output>entity_list</output>
    </operator>
    <operator id="1">
        <instruction>Extract relevant facts from the context that directly answer the question.</instruction>
        <input>entity_list, context</input>
        <output>relevant_facts</output>
    </operator>
    <operator id="2">
        <instruction>Verify that the extracted facts contain a direct answer to the question.</instruction>
        <input>relevant_facts</input>
        <output>answer_candidate</output>
    </operator>
    <operator id="3">
        <instruction>Check for any ambiguity or missing information that might affect the correctness of the answer.</instruction>
        <input>answer_candidate</input>
        <output>final_answer</output>
    </operator>
    <operator id="4">
        <instruction>Validate the final answer against all provided context to ensure consistency.</instruction>
        <input>final_answer, context</input>
        <output>validated_answer</output>
    </operator>
    <operator id="5">
        <instruction>Return the validated answer as the solution to the problem.</instruction>
        <input>validated_answer</input>
        <output>solution</output>
    </operator>