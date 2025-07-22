# Workflow ID: drop_207_0
# Benchmark: drop
# Data Indices: [2124, 2411, 1432, 868, 1449]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
    </node>
    <node id="3" type="agent">
        <instruction>Identify the specific values needed to answer the question by analyzing the context of the query.</instruction>
    </node>
    <node id="4" type="agent">
        <instruction>Perform necessary arithmetic operations or comparisons based on the extracted values.</instruction>
    </node>
    <node id="5" type="agent">
        <instruction>Validate that the computed result aligns with the question's requirements and constraints.</instruction>
    </node>
    <node id="6" type="output">
        <data>final_answer</data>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>