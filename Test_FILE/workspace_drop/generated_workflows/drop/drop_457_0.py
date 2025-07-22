# Workflow ID: drop_457_0
# Benchmark: drop
# Data Indices: [2836, 1312, 2786, 727]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key elements in the passage related to the question. Extract all relevant numerical or descriptive data points that could help answer the question.</instruction>
        <input>1</input>
        <output>extracted_data</output>
    </node>
    <node id="3" type="agent">
        <instruction>Compare and rank the extracted values based on the query's requirement (e.g., longest field goal, most common household type, etc.). Ensure only relevant comparisons are made.</instruction>
        <input>2</input>
        <output>ranked_values</output>
    </node>
    <node id="4" type="agent">
        <instruction>Determine the specific answer by locating the position (e.g., quarter, category, player) associated with the ranked value from the previous step.</instruction>
        <input>3</input>
        <output>final_answer</output>
    </node>
    <node id="5" type="output">
        <input>4</input>
    </node>