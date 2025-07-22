# Workflow ID: drop_113_0
# Benchmark: drop
# Data Indices: [2997, 726, 3444, 2419]

<node id="1" type="input">
        <parameter>problem</parameter>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage that relates to the question.</instruction>
        <input>1</input>
        <output>extracted_data</output>
    </node>
    <node id="3" type="agent">
        <instruction>Identify the key values needed to solve the problem based on the extracted data. Think step by step: first, determine what is being asked; second, locate the necessary numbers in the data; third, perform the required calculation.</instruction>
        <input>2</input>
        <output>calculated_answer</output>
    </node>
    <node id="4" type="agent">
        <instruction>Verify the correctness of the calculated answer by cross-checking with the original passage and ensuring logical consistency.</instruction>
        <input>3</input>
        <output>verified_answer</output>
    </node>
    <node id="5" type="output">
        <input>4</input>
        <output>final_answer</output>
    </node>