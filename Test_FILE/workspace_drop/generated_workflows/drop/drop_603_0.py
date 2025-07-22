# Workflow ID: drop_603_0
# Benchmark: drop
# Data Indices: [1049, 5, 240, 2490]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage that pertains to the question.</instruction>
        <input>1</input>
    </node>
    <node id="3" type="agent">
        <instruction>Perform necessary arithmetic operations or comparisons based on the extracted data to answer the question.</instruction>
        <input>2</input>
    </node>
    <node id="4" type="agent">
        <instruction>Verify the correctness of the calculation by cross-checking with the original passage.</instruction>
        <input>3</input>
    </node>
    <node id="5" type="output">
        <instruction>Return the final answer in the required format (e.g., number, percentage, etc.).</instruction>
        <input>4</input>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>