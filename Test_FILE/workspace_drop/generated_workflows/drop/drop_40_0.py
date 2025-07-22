# Workflow ID: drop_40_0
# Benchmark: drop
# Data Indices: [3089, 1688, 1523, 308, 648]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
    </node>
    <node id="3" type="agent">
        <instruction>Identify the specific values needed to answer the question by analyzing the context of the query.</instruction>
    </node>
    <node id="4" type="agent">
        <instruction>Perform the necessary arithmetic operation (e.g., subtraction, addition) using the extracted values.</instruction>
    </node>
    <node id="5" type="agent">
        <instruction>Verify the result by cross-checking with the original passage to ensure accuracy.</instruction>
    </node>
    <node id="6" type="output">
        <description>Return the final computed answer as a single number or value.</description>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>