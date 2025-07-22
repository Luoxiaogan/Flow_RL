# Workflow ID: drop_328_0
# Benchmark: drop
# Data Indices: [3770, 3523, 3577, 2051, 1450]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Extract all relevant numerical values from the passage related to the question. Identify the key metrics (e.g., yardages) and their context.</instruction>
        <input>1</input>
    </node>
    <node id="3" type="agent">
        <instruction>For each metric, determine whether it is part of the comparison required by the question. Filter out irrelevant data based on the question's focus.</instruction>
        <input>2</input>
    </node>
    <node id="4" type="agent">
        <instruction>Identify the maximum and minimum values among the filtered metrics. Compute the difference between them if the question asks for a comparison.</instruction>
        <input>3</input>
    </node>
    <node id="5" type="agent">
        <instruction>Validate that the computed result matches the question's requirement. If the question involves multiple comparisons (e.g., first vs third pass), ensure the correct indices are used.</instruction>
        <input>4</input>
    </node>
    <node id="6" type="output">
        <data>5</data>
        <input>5</input>
    </node>