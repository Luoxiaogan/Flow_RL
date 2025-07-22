# Workflow ID: drop_104_0
# Benchmark: drop
# Data Indices: [732, 1747, 1949, 3967, 3989]

<node id="1" type="input">
        <param>problem</param>
    </node>
    <node id="2" type="agent">
        <instruction>Extract the key numerical data from the passage relevant to the question. Identify specific values, counts, or percentages mentioned.</instruction>
        <input>problem</input>
        <output>extracted_data</output>
    </node>
    <node id="3" type="agent">
        <instruction>Map the extracted data to the exact question being asked. Determine which value directly answers the query or requires a simple calculation (e.g., subtraction, percentage).</instruction>
        <input>extracted_data</input>
        <output>mapped_value</output>
    </node>
    <node id="4" type="agent">
        <instruction>Verify that the mapped value is logically consistent with the context of the passage and matches the required format (integer, percentage, etc.). If multiple values exist, ensure only one is selected based on the question's focus.</instruction>
        <input>mapped_value</input>
        <output>verified_answer</output>
    </node>
    <node id="5" type="output">
        <input>verified_answer</input>
    </node>