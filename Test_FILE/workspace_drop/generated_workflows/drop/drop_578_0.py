# Workflow ID: drop_578_0
# Benchmark: drop
# Data Indices: [2413, 1692, 2117, 43]

<node id="1" type="input">
        <param name="problem" />
    </node>
    <node id="2" type="agent">
        <instruction>
            Analyze the problem step by step. Identify the key numerical data and what is being asked. Determine if any arithmetic or logical operations are needed to derive the answer.
        </instruction>
        <input>1</input>
        <output>analysis</output>
    </node>
    <node id="3" type="agent">
        <instruction>
            Based on the analysis, extract the relevant numbers and determine the mathematical operation required to solve the question. Ensure that the operation aligns with the problem's context (e.g., percentages, differences, totals).
        </instruction>
        <input>2</input>
        <output>calculation</output>
    </node>
    <node id="4" type="agent">
        <instruction>
            Perform the calculation using the extracted values. Double-check for accuracy and ensure the result is in the correct format (e.g., percentage, integer, decimal).
        </instruction>
        <input>3</input>
        <output>result</output>
    </node>
    <node id="5" type="output">
        <input>4</input>
    </node>