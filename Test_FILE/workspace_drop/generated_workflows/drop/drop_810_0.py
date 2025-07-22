# Workflow ID: drop_810_0
# Benchmark: drop
# Data Indices: [189, 2246, 3349, 1564]

<node id="1" type="input">
        <parameter>problem</parameter>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage. Identify the key values needed to solve the question step by step.</instruction>
        <input>1</input>
        <output>extracted_data</output>
    </node>
    <node id="3" type="agent">
        <instruction>Perform the necessary mathematical operations using the extracted data to answer the question. Ensure all steps are logically connected and correct.</instruction>
        <input>2</input>
        <output>result</output>
    </node>
    <node id="4" type="agent">
        <instruction>Verify the result by cross-checking with the original passage and ensuring no data was misinterpreted or omitted.</instruction>
        <input>3</input>
        <output>verified_result</output>
    </node>
    <node id="5" type="output">
        <input>4</input>
        <output>final_answer</output>
    </node>