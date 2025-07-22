# Workflow ID: hotpotqa_30_0
# Benchmark: hotpotqa
# Data Indices: [2328, 3943, 1695, 2720, 2260]

<operator id="0">
        <instruction>Identify the key entities and relationships in the problem context to determine the correct answer.</instruction>
        <input>problem</input>
        <output>entity_list</output>
    </operator>
    <operator id="1">
        <instruction>Extract the relevant actor or character from the context who matches the role or description in the question.</instruction>
        <input>entity_list</input>
        <output>candidate_actor</output>
    </operator>
    <operator id="2">
        <instruction>Verify that the candidate actor's most famous role aligns with the description provided in the question.</instruction>
        <input>candidate_actor</input>
        <output>verified_actor</output>
    </operator>
    <operator id="3">
        <instruction>Ensure the verified actor is associated with the specified show or film mentioned in the question.</instruction>
        <input>verified_actor</input>
        <output>final_answer</output>
    </operator>