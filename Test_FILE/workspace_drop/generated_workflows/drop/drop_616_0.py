# Workflow ID: drop_616_0
# Benchmark: drop
# Data Indices: [1711, 140, 2843, 772]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage based on the question.</instruction>
    </node>
    <node id="3" type="agent">
        <instruction>Perform arithmetic or logical operations to derive the final answer from the extracted data.</instruction>
    </node>
    <node id="4" type="output">
        <data>final_answer</data>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>