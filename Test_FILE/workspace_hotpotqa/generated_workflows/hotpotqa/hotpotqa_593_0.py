# Workflow ID: hotpotqa_593_0
# Benchmark: hotpotqa
# Data Indices: [982, 3171, 3466, 343]

<operator id="0">
        <instruction>Identify the key entities in the problem statement and determine what is being asked.</instruction>
        <input>problem</input>
        <output>key_entities, question_focus</output>
    </operator>
    <operator id="1">
        <instruction>Extract relevant context information that directly relates to the key entities identified.</instruction>
        <input>context, key_entities</input>
        <output>relevant_context</output>
    </operator>
    <operator id="2">
        <instruction>Process the relevant context to find a direct match or logical inference for the answer.</instruction>
        <input>relevant_context</input>
        <output>candidate_answer</output>
    </operator>
    <operator id="3">
        <instruction>Verify the candidate answer against all available context to ensure accuracy and avoid contradictions.</instruction>
        <input>relevant_context, candidate_answer</input>
        <output>final_answer</output>
    </operator>
    <operator id="4">
        <instruction>Ensure the final answer is formatted correctly and matches the expected output type (e.g., string, list).</instruction>
        <input>final_answer</input>
        <output>formatted_output</output>
    </operator>
    <edge from="0" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>