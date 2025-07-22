# Workflow ID: hotpotqa_115_0
# Benchmark: hotpotqa
# Data Indices: [583, 158, 852, 818]

<operator id="1">
        <instruction>Identify the key entities and relationships in the problem context to determine the correct answer.</instruction>
        <input>problem</input>
        <output>entity_list</output>
    </operator>
    <operator id="2">
        <instruction>Extract relevant facts from the context that directly relate to the question being asked.</instruction>
        <input>entity_list, context</input>
        <output>relevant_facts</output>
    </operator>
    <operator id="3">
        <instruction>Compare the extracted facts to determine which entity satisfies the condition in the question.</instruction>
        <input>relevant_facts</input>
        <output>comparison_result</output>
    </operator>
    <operator id="4">
        <instruction>Validate the comparison result against known constraints or definitions in the context (e.g., dates, roles, locations).</instruction>
        <input>comparison_result, context</input>
        <output>validated_answer</output>
    </operator>
    <operator id="5">
        <instruction>Ensure the final answer is unambiguous and derived solely from the validated information.</instruction>
        <input>validated_answer</input>
        <output>final_answer</output>
    </operator>