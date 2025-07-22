# Workflow ID: drop_572_0
# Benchmark: drop
# Data Indices: [2049, 2896, 303, 2793, 1850]

<node id="1" type="input">
        <parameter>problem</parameter>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical data points in the passage that relate to the question. Break down the problem step by step.</instruction>
        <input>1</input>
    </node>
    <node id="3" type="agent">
        <instruction>Verify the relevance of each identified data point to the specific question being asked. Eliminate any irrelevant information.</instruction>
        <input>2</input>
    </node>
    <node id="4" type="agent">
        <instruction>Perform the necessary arithmetic or logical operations using the verified data points to compute the answer.</instruction>
        <input>3</input>
    </node>
    <node id="5" type="agent">
        <instruction>Check for consistency between the computed result and the context of the passage to ensure accuracy.</instruction>
        <input>4</input>
    </node>
    <node id="6" type="output">
        <input>5</input>
    </node>