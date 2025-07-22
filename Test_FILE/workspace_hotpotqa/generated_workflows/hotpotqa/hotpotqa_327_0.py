# Workflow ID: hotpotqa_327_0
# Benchmark: hotpotqa
# Data Indices: [3498, 2162, 486, 1484, 2880]

<agent id="1">
        <instruction>Identify the key entities in the problem and extract relevant contextual information.</instruction>
        <input>problem</input>
        <output>entity_list</output>
    </agent>
    <agent id="2">
        <instruction>Map each entity to its corresponding data point or attribute in the context.</instruction>
        <input>entity_list</input>
        <output>mapped_data</output>
    </agent>
    <agent id="3">
        <instruction>Apply logical deduction to connect mapped data points based on the question's requirements.</instruction>
        <input>mapped_data</input>
        <output>deduced_answer</output>
    </agent>
    <agent id="4">
        <instruction>Validate the deduced answer against all provided context to ensure accuracy.</instruction>
        <input>deduced_answer</input>
        <output>validated_answer</output>
    </agent>
    <agent id="5">
        <instruction>Format the final answer to match the expected output structure for this problem type.</instruction>
        <input>validated_answer</input>
        <output>final_output</output>
    </agent>
    <connection from="1" to="2"/>
    <connection from="2" to="3"/>
    <connection from="3" to="4"/>
    <connection from="4" to="5"/>