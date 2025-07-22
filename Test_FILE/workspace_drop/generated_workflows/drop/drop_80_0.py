# Workflow ID: drop_80_0
# Benchmark: drop
# Data Indices: [3960, 2383, 257, 831, 1308]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical data in the passage relevant to the question. Break down the problem step by step.</instruction>
        <input>1</input>
    </node>
    <node id="3" type="agent">
        <instruction>Extract percentages or counts from the passage that relate to the question. Ensure accuracy and relevance.</instruction>
        <input>2</input>
    </node>
    <node id="4" type="agent">
        <instruction>Calculate the required percentage by subtracting the given category from 100%. Show each step clearly.</instruction>
        <input>3</input>
    </node>
    <node id="5" type="agent">
        <instruction>Verify that the calculation aligns with the context of the passage and confirms the final answer.</instruction>
        <input>4</input>
    </node>
    <node id="6" type="output">
        <input>5</input>
    </node>