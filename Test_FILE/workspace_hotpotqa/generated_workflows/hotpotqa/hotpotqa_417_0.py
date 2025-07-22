# Workflow ID: hotpotqa_417_0
# Benchmark: hotpotqa
# Data Indices: [2808, 3458, 1622, 1700, 15]

<operator id="0">
        <instruction>Identify the key entities and relationships in the problem context to determine what needs to be extracted.</instruction>
        <input>problem</input>
        <output>entity_list</output>
    </operator>
    <operator id="1">
        <instruction>Extract specific details from the context that directly answer the question. Focus only on relevant facts.</instruction>
        <input>entity_list, context</input>
        <output>candidate_answer</output>
    </operator>
    <operator id="2">
        <instruction>Validate the candidate answer by cross-referencing with other parts of the context to ensure accuracy and avoid misinterpretation.</instruction>
        <input>candidate_answer, context</input>
        <output>validated_answer</output>
    </operator>
    <operator id="3">
        <instruction>Ensure the final answer is precise and matches the format required by the question (e.g., date, name, event).</instruction>
        <input>validated_answer</input>
        <output>final_answer</output>
    </operator>