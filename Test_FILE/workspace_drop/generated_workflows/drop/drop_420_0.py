# Workflow ID: drop_420_0
# Benchmark: drop
# Data Indices: [884, 415, 1309, 206]

<node id="1" type="input">
        <param name="problem">self.problem</param>
    </node>
    <node id="2" type="agent">
        <instruction>Identify all relevant numerical values in the passage that relate to the question. Extract each value and its context.</instruction>
        <input>1</input>
        <output>extracted_values</output>
    </node>
    <node id="3" type="agent">
        <instruction>From the extracted values, determine which ones correspond to the quantities needed to answer the question. Filter out irrelevant data based on the question's focus.</instruction>
        <input>2</input>
        <output>filtered_values</output>
    </node>
    <node id="4" type="agent">
        <instruction>Perform the necessary arithmetic operation (e.g., subtraction) to compute the difference between the longest and shortest values relevant to the question.</instruction>
        <input>3</input>
        <output>computed_difference</output>
    </node>
    <node id="5" type="agent">
        <instruction>Verify that the computed difference aligns with the question's requirement — for example, confirming it is the yardage difference between the longest and shortest touchdown passes.</instruction>
        <input>4</input>
        <output>final_answer</output>
    </node>
    <node id="6" type="output">
        <input>5</input>
    </node>