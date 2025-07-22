# Workflow ID: drop_718_0
# Benchmark: drop
# Data Indices: [1445, 599, 1144, 3631, 193]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical values from the passage related to the question.</instruction>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="agent">
        <instruction>Perform the required mathematical operation (e.g., subtraction, comparison) using the extracted values.</instruction>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="agent">
        <instruction>Validate the result by cross-checking with the passage context to ensure accuracy.</instruction>
        <depends_on>3</depends_on>
    </node>
    <node id="5" type="output">
        <connects_to>4</connects_to>
    </node>