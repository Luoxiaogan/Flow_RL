# Workflow ID: drop_472_0
# Benchmark: drop
# Data Indices: [1510, 2695, 1738, 2181, 3237]

<node id="1" type="input">
        <parameter>problem</parameter>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical data points relevant to the question. Break down the passage to locate exact values or formulas needed.</instruction>
        <input>1</input>
        <output>key_data_points</output>
    </node>
    <node id="3" type="agent">
        <instruction>Apply mathematical operations or logical deductions using the extracted data to compute the answer step by step.</instruction>
        <input>2</input>
        <output>computed_answer</output>
    </node>
    <node id="4" type="agent">
        <instruction>Verify that the computed answer aligns with the question's requirements and matches the context of the passage.</instruction>
        <input>3</input>
        <output>verified_answer</output>
    </node>
    <node id="5" type="output">
        <input>4</input>
        <output>final_answer</output>
    </node>