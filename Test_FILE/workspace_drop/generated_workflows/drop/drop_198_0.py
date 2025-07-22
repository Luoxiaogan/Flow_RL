# Workflow ID: drop_198_0
# Benchmark: drop
# Data Indices: [103, 3635, 3281, 2086, 1867]

<operator id="0">
        <instruction>Identify the key numerical data points in the passage related to the question.</instruction>
        <input>problem</input>
        <output>key_data_points</output>
    </operator>
    <operator id="1">
        <instruction>Extract all relevant values that match the query type (e.g., yards, scores, years).</instruction>
        <input>key_data_points</input>
        <output>extracted_values</output>
    </operator>
    <operator id="2">
        <instruction>Filter and validate values based on context—only include those directly answering the question.</instruction>
        <input>extracted_values</input>
        <output>filtered_values</output>
    </operator>
    <operator id="3">
        <instruction>Sum or compute required total from filtered values if multiple items are involved.</instruction>
        <input>filtered_values</input>
        <output>final_answer</output>
    </operator>
    <operator id="4">
        <instruction>Verify final answer matches expected format and logic of the question.</instruction>
        <input>final_answer</input>
        <output>verified_answer</output>
    </operator>
    <edge from="0" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>