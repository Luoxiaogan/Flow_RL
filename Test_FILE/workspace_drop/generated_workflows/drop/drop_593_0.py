# Workflow ID: drop_593_0
# Benchmark: drop
# Data Indices: [3394, 3200, 3812, 2623]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="process">
        <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
    </node>
    <node id="3" type="process">
        <instruction>Perform necessary calculations (e.g., percentages, differences, ratios) based on extracted data.</instruction>
    </node>
    <node id="4" type="validate">
        <instruction>Verify that the calculation aligns with the question's requirements and uses correct data sources.</instruction>
    </node>
    <node id="5" type="output">
        <instruction>Return the final answer in the required format (e.g., percentage, number, etc.).</instruction>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>