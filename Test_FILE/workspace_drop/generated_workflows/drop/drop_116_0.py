# Workflow ID: drop_116_0
# Benchmark: drop
# Data Indices: [2266, 883, 2135, 1086, 320]

<node id="1" type="input">
        <parameter>problem</parameter>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical values relevant to the question in the passage.</instruction>
        <input>1</input>
        <output>key_values</output>
    </node>
    <node id="3" type="agent">
        <instruction>Perform the required calculation or comparison based on the key values. Think step by step: first, determine what is being asked; second, extract or compute the necessary numbers; third, apply the correct operation (e.g., subtraction, percentage, ratio).</instruction>
        <input>2</input>
        <output>result</output>
    </node>
    <node id="4" type="agent">
        <instruction>Verify that the result matches the question's requirement and format it appropriately (e.g., as a number, percentage, or difference).</instruction>
        <input>3</input>
        <output>final_answer</output>
    </node>
    <node id="5" type="output">
        <input>4</input>
    </node>