# Workflow ID: drop_660_0
# Benchmark: drop
# Data Indices: [947, 216, 2019, 2785]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify all field goals mentioned in the passage and extract their yardages.</instruction>
        <input>1</input>
    </node>
    <node id="3" type="agent">
        <instruction>From the extracted yardages, determine the longest field goal by comparing each value step by step.</instruction>
        <input>2</input>
    </node>
    <node id="4" type="output">
        <data>3</data>
        <input>3</input>
    </node>