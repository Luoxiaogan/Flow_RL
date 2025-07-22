# Workflow ID: hotpotqa_587_0
# Benchmark: hotpotqa
# Data Indices: [1088, 285, 2395, 3930, 1118]

<operator id="0">
        <instruction>Identify the birth year of M. Shadows and D. S. Bradford from the context provided.</instruction>
        <input>problem</input>
        <output>birth_years</output>
    </operator>
    <operator id="1">
        <instruction>Compare the birth years to determine who was born first.</instruction>
        <input>birth_years</input>
        <output>earlier_birth</output>
    </operator>
    <operator id="2">
        <instruction>Return the name of the artist born first.</instruction>
        <input>earlier_birth</input>
        <output>final_answer</output>
    </operator>