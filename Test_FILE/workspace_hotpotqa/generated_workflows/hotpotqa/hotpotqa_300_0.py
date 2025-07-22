# Workflow ID: hotpotqa_300_0
# Benchmark: hotpotqa
# Data Indices: [3700, 3707, 2102, 1764, 1275]

<start/>
    <agent id="1" type="reasoning">
        <instruction>Step 1: Identify the key entities and relationships in the context. Focus on the question and extract relevant facts.</instruction>
        <input>problem</input>
        <output>step1_output</output>
    </agent>
    <agent id="2" type="filter">
        <instruction>Step 2: Filter out irrelevant information from step1_output to focus only on the necessary data for answering the question.</instruction>
        <input>step1_output</input>
        <output>step2_output</output>
    </agent>
    <agent id="3" type="logic">
        <instruction>Step 3: Apply logical deduction using the filtered data to determine the correct answer.</instruction>
        <input>step2_output</input>
        <output>step3_output</output>
    </agent>
    <agent id="4" type="verify">
        <instruction>Step 4: Verify the solution by cross-checking with the original context to ensure accuracy.</instruction>
        <input>step3_output</input>
        <output>final_answer</output>
    </agent>
    <end/>