# Workflow ID: drop_316_0
# Benchmark: drop
# Data Indices: [1561, 295, 2854, 3179]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the relevant numerical values from the passage related to the question. Extract the yardage for each touchdown mentioned.</instruction>
        <input>1</input>
        <output>yardages</output>
    </node>
    <node id="3" type="agent">
        <instruction>Calculate the difference between Reggie Wayne's touchdown and Dallas Clark's first touchdown by subtracting the smaller value from the larger one.</instruction>
        <input>2</input>
        <output>difference</output>
    </node>
    <node id="4" type="output">
        <input>3</input>
        <output>final_answer</output>
    </node>