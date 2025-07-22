# Workflow ID: drop_375_0
# Benchmark: drop
# Data Indices: [1418, 1456, 2278, 1538]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="process">
        <instruction>Extract relevant numerical data from the passage based on the question.</instruction>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="process">
        <instruction>Identify and calculate the required value using the extracted data (e.g., sum, percentage, max).</instruction>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="output">
        <instruction>Return the final computed answer as a number or percentage.</instruction>
        <depends_on>3</depends_on>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>