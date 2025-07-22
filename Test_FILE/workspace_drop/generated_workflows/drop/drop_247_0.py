# Workflow ID: drop_247_0
# Benchmark: drop
# Data Indices: [1521, 1767, 381, 2138]

<node id="1" type="input">
        <prompt>Understand the question and identify key elements needed for calculation.</prompt>
    </node>
    <node id="2" type="process">
        <prompt>Extract relevant percentages from the passage that contribute to the final answer.</prompt>
    </node>
    <node id="3" type="process">
        <prompt>Calculate the percentage of non-British Chinese population by subtracting British Chinese percentage from 100%.</prompt>
    </node>
    <node id="4" type="output">
        <prompt>Return the calculated percentage of the United Kingdom in 2011 that are not British Chinese.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>