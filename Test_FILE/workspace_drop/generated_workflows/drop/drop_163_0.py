# Workflow ID: drop_163_0
# Benchmark: drop
# Data Indices: [2168, 3720, 3571, 2323]

<node id="1" type="input">
        <prompt>Read the passage carefully and identify all numerical values related to the question.</prompt>
    </node>
    <node id="2" type="process">
        <prompt>Extract relevant data points that answer the specific question. For example, if the question asks about field goal distances, find all field goal yardages mentioned.</prompt>
    </node>
    <node id="3" type="process">
        <prompt>Perform arithmetic operations (e.g., subtraction, comparison) based on the extracted values to compute the final answer.</prompt>
    </node>
    <node id="4" type="output">
        <prompt>Return the computed result as a single number or value.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>