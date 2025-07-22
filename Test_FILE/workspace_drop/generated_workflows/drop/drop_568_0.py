# Workflow ID: drop_568_0
# Benchmark: drop
# Data Indices: [2640, 477, 3347, 1804, 2780]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
    </node>
    <node id="3" type="agent">
        <instruction>Identify the specific values needed to answer the question based on the extracted data.</instruction>
    </node>
    <node id="4" type="agent">
        <instruction>Perform the required arithmetic or logical operation to derive the answer.</instruction>
    </node>
    <node id="5" type="agent">
        <instruction>Verify that the computed result matches the context of the question and is logically sound.</instruction>
    </node>
    <node id="6" type="output">
        <data>final_answer</data>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>