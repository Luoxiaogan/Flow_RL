# Workflow ID: drop_645_0
# Benchmark: drop
# Data Indices: [1296, 2866, 162, 3893, 2021]

<operator id="0">
        <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
        <input>problem</input>
        <output>raw_data</output>
    </operator>
    <operator id="1">
        <instruction>Identify and isolate the values that directly answer the question. If multiple values exist, determine which one is most relevant or perform a calculation if needed.</instruction>
        <input>raw_data</input>
        <output>relevant_values</output>
    </operator>
    <operator id="2">
        <instruction>Apply arithmetic operations (e.g., subtraction, comparison) to derive the final answer based on the relevant values.</instruction>
        <input>relevant_values</input>
        <output>final_answer</output>
    </operator>
    <operator id="3">
        <instruction>Verify that the final answer matches the question's requirement and format (e.g., integer, percentage, etc.).</instruction>
        <input>final_answer</input>
        <output>validated_answer</output>
    </operator>
    <operator id="4">
        <instruction>Ensure no extraneous information is included in the final output; only return the required value as specified by the question.</instruction>
        <input>validated_answer</input>
        <output>clean_output</output>
    </operator>