# Workflow ID: drop_529_0
# Benchmark: drop
# Data Indices: [321, 1041, 2899, 1720]

<node id="1" type="input">
        <prompt>Extract the relevant numerical data from the passage that answers the question.</prompt>
    </node>
    <node id="2" type="process">
        <prompt>Identify the values for the quantities mentioned in the question. For example, if the question asks for a difference, find both numbers involved in the subtraction.</prompt>
    </node>
    <node id="3" type="compute">
        <prompt>Perform the required arithmetic operation (e.g., subtraction, addition) to compute the answer based on the extracted values.</prompt>
    </node>
    <node id="4" type="validate">
        <prompt>Check that the computed result matches the context of the question and is logically consistent with the passage.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final numerical answer as the solution to the question.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>