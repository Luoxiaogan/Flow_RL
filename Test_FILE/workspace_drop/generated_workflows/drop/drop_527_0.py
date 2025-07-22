# Workflow ID: drop_527_0
# Benchmark: drop
# Data Indices: [220, 3294, 2092, 3804, 1512]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical value in the passage related to the question.</instruction>
        <input>1</input>
        <output>key_value</output>
    </node>
    <node id="3" type="agent">
        <instruction>Calculate the complementary percentage by subtracting the given percentage from 100.</instruction>
        <input>2</input>
        <output>complement_percentage</output>
    </node>
    <node id="4" type="output">
        <input>3</input>
        <output>final_answer</output>
    </node>