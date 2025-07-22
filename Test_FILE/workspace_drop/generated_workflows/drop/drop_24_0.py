# Workflow ID: drop_24_0
# Benchmark: drop
# Data Indices: [3533, 819, 1505, 712]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the relevant passage and extract all touchdown pass yardages mentioned.</instruction>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="agent">
        <instruction>From the extracted yardages, determine the maximum value by comparing each one step-by-step.</instruction>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="output">
        <instruction>Return the longest touchdown pass yardage as the final answer.</instruction>
        <depends_on>3</depends_on>
    </node>