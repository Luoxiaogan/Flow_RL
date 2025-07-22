# Workflow ID: drop_764_0
# Benchmark: drop
# Data Indices: [3962, 3127, 2084, 2860, 1221]

<operator id="1" type="extract">
        <input>problem</input>
        <output>extracted_data</output>
        <instruction>Identify and extract all numerical values related to field goals, touchdowns, and yardages from the passage.</instruction>
    </operator>
    
    <operator id="2" type="filter">
        <input>extracted_data</input>
        <output>relevant_values</output>
        <instruction>Filter out only the values that represent field goal distances or touchdown pass lengths.</instruction>
    </operator>
    
    <operator id="3" type="find_max">
        <input>relevant_values</input>
        <output>longest_value</output>
        <instruction>Determine the maximum value among the filtered yardage numbers.</instruction>
    </operator>
    
    <operator id="4" type="summarize">
        <input>longest_value</input>
        <output>combined_total</output>
        <instruction>Sum the longest field goal and the longest defensive touchdown if both exist; otherwise return just the longest value.</instruction>
    </operator>
    
    <operator id="5" type="validate">
        <input>combined_total</input>
        <output>final_answer</output>
        <instruction>Ensure the final answer is a single numeric value representing the combined yards of the longest field goal and the longest defensive touchdown.</instruction>
    </operator>