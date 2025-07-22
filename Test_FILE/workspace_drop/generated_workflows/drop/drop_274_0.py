# Workflow ID: drop_274_0
# Benchmark: drop
# Data Indices: [3535, 2890, 3258, 2511]

<node id="1" type="input">
        <parameter>problem</parameter>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the relevant data in the passage that answers the question. Think step by step: first locate the key information, then determine what needs to be calculated.</instruction>
        <input>1</input>
        <output>retrieved_data</output>
    </node>
    <node id="3" type="agent">
        <instruction>Perform the necessary calculation using the retrieved data. Ensure the steps are clear and logical.</instruction>
        <input>2</input>
        <output>calculation_result</output>
    </node>
    <node id="4" type="agent">
        <instruction>Verify the correctness of the calculation. Double-check each step and confirm the final answer matches the question asked.</instruction>
        <input>3</input>
        <output>verified_answer</output>
    </node>
    <node id="5" type="output">
        <input>4</input>
        <output>final_answer</output>
    </node>