# Workflow ID: drop_729_0
# Benchmark: drop
# Data Indices: [2343, 1213, 879, 3918]

<node id="1" type="input">
        <param name="problem" />
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage based on the question. Identify all values mentioned that relate to the query.</instruction>
        <input>1</input>
        <output>extracted_data</output>
    </node>
    <node id="3" type="agent">
        <instruction>Perform necessary calculations using the extracted data. If the question involves a difference, compute it step by step.</instruction>
        <input>2</input>
        <output>calculated_result</output>
    </node>
    <node id="4" type="agent">
        <instruction>Verify the correctness of the calculation by cross-checking with the original passage context.</instruction>
        <input>3</input>
        <output>verified_result</output>
    </node>
    <node id="5" type="output">
        <input>4</input>
        <output>final_answer</output>
    </node>