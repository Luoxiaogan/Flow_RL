# Workflow ID: drop_624_0
# Benchmark: drop
# Data Indices: [2632, 2468, 2987, 1069, 1570]

<node id="1" type="input">
        <prompt>Extract relevant numerical data from the passage related to the question.</prompt>
    </node>
    <node id="2" type="process">
        <prompt>Identify the specific values or calculations needed to answer the question based on the extracted data.</prompt>
    </node>
    <node id="3" type="validate">
        <prompt>Verify that all necessary data has been correctly interpreted and no steps are missing in the calculation.</prompt>
    </node>
    <node id="4" type="compute">
        <prompt>Perform the required arithmetic operations step-by-step to derive the final answer.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the computed result as the final answer, ensuring it matches the question's requirement.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>