# Workflow ID: hotpotqa_316_0
# Benchmark: hotpotqa
# Data Indices: [2988, 1644, 3845, 2810]

<operator id="1">
        <instruction>Identify the key elements in the question and determine what type of information is being sought.</instruction>
        <input>problem</input>
        <output>key_elements</output>
    </operator>
    <operator id="2">
        <instruction>Extract relevant context that directly addresses the question based on the key elements.</instruction>
        <input>key_elements, context</input>
        <output>relevant_info</output>
    </operator>
    <operator id="3">
        <instruction>Compare and validate the extracted information against the known facts to ensure accuracy.</instruction>
        <input>relevant_info</input>
        <output>validated_answer</output>
    </operator>
    <operator id="4">
        <instruction>Format the final answer clearly and concisely based on the validated result.</instruction>
        <input>validated_answer</input>
        <output>final_output</output>
    </operator>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>