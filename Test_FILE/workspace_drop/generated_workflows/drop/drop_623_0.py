# Workflow ID: drop_623_0
# Benchmark: drop
# Data Indices: [2449, 2965, 1005, 2010]

<node id="1" type="input">
        <parameter>problem</parameter>
    </node>
    <node id="2" type="agent">
        <instruction>Extract the relevant numerical data from the passage that answers the question. Identify the key values and their context.</instruction>
        <input>1</input>
        <output>extracted_data</output>
    </node>
    <node id="3" type="agent">
        <instruction>Compare the extracted values to determine the difference or relationship required by the question. Perform arithmetic operations if needed.</instruction>
        <input>2</input>
        <output>calculated_result</output>
    </node>
    <node id="4" type="agent">
        <instruction>Verify the calculation by cross-referencing with the original passage to ensure accuracy and avoid misinterpretation.</instruction>
        <input>3</input>
        <output>verified_result</output>
    </node>
    <node id="5" type="output">
        <input>4</input>
        <output>final_answer</output>
    </node>