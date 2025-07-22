# Workflow ID: drop_192_0
# Benchmark: drop
# Data Indices: [1260, 3637, 1513, 950]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage that relates to the question. Identify key statistics, such as scores, yardages, percentages, or counts mentioned in the context of the question.</instruction>
        <input>1</input>
    </node>
    <node id="3" type="agent">
        <instruction>Identify the specific value being asked for in the question. For example, if the question asks about a field goal distance, locate the longest yardage mentioned in the passage related to field goals.</instruction>
        <input>2</input>
    </node>
    <node id="4" type="agent">
        <instruction>Verify the extracted value by cross-checking with all mentions in the passage. Ensure no other value exceeds it—this confirms correctness.</instruction>
        <input>3</input>
    </node>
    <node id="5" type="output">
        <instruction>Return the final answer based on the verified value. Do not include any explanation or extra text—only the numeric result.</instruction>
        <input>4</input>
    </node>