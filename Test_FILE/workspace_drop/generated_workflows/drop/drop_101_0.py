# Workflow ID: drop_101_0
# Benchmark: drop
# Data Indices: [1216, 2911, 2435, 1475]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical data points relevant to the question. Extract all values that could contribute to answering the query.</instruction>
        <input>1</input>
        <output>2</output>
    </node>
    <node id="3" type="agent">
        <instruction>For each value extracted, determine its relevance to the specific question asked. Filter out irrelevant data based on context.</instruction>
        <input>2</input>
        <output>3</output>
    </node>
    <node id="4" type="agent">
        <instruction>Perform necessary arithmetic or logical operations using the filtered values to compute the final answer.</instruction>
        <input>3</input>
        <output>4</output>
    </node>
    <node id="5" type="agent">
        <instruction>Verify the computed result by cross-checking with original passage details to ensure accuracy and avoid calculation errors.</instruction>
        <input>4</input>
        <output>5</output>
    </node>
    <node id="6" type="output">
        <input>5</input>
    </node>