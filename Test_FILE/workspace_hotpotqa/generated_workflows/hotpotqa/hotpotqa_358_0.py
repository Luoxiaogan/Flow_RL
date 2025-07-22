# Workflow ID: hotpotqa_358_0
# Benchmark: hotpotqa
# Data Indices: [978, 2276, 2195, 501]

<operator id="0">
        <instruction>Identify the key entities and relationships in the problem context to determine the correct answer.</instruction>
        <input>problem</input>
        <output>step_1_output</output>
    </operator>
    <operator id="1">
        <instruction>Extract relevant facts from the context that directly relate to the question being asked.</instruction>
        <input>step_1_output</input>
        <output>step_2_output</output>
    </operator>
    <operator id="2">
        <instruction>Compare each candidate answer against the extracted facts to find the one that matches the question's criteria.</instruction>
        <input>step_2_output</input>
        <output>step_3_output</output>
    </operator>
    <operator id="3">
        <instruction>Validate the selected answer by cross-referencing it with all available context to ensure consistency.</instruction>
        <input>step_3_output</input>
        <output>final_answer</output>
    </operator>