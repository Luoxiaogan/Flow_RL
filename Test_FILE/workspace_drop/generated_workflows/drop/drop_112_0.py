# Workflow ID: drop_112_0
# Benchmark: drop
# Data Indices: [756, 2562, 1556, 635]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Think step by step. Identify the key information needed to solve this problem. Extract numerical values, timeframes, or relationships that are essential.</instruction>
        <input>1</input>
        <output>key_info</output>
    </node>
    <node id="3" type="agent">
        <instruction>Based on the extracted information, determine the mathematical relationship or logic required to compute the answer. If multiple steps are involved, break them down clearly.</instruction>
        <input>2</input>
        <output>calculation_logic</output>
    </node>
    <node id="4" type="agent">
        <instruction>Apply the logic from the previous step to derive the final answer. Ensure all intermediate steps are logically sound and consistent with the input data.</instruction>
        <input>3</input>
        <output>final_answer</output>
    </node>
    <node id="5" type="output">
        <input>4</input>
    </node>