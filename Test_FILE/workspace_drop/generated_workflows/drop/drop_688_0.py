# Workflow ID: drop_688_0
# Benchmark: drop
# Data Indices: [1121, 2981, 2306, 1899, 2350]

<node id="1" type="input">
        <prompt>Understand the question and identify key numerical data needed to solve it.</prompt>
    </node>
    <node id="2" type="process">
        <prompt>Extract relevant numbers from the passage based on the question.</prompt>
    </node>
    <node id="3" type="process">
        <prompt>Perform necessary calculations or comparisons using the extracted data.</prompt>
    </node>
    <node id="4" type="output">
        <prompt>Return the final answer based on the processed result.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>