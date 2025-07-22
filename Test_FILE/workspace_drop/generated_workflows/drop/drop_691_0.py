# Workflow ID: drop_691_0
# Benchmark: drop
# Data Indices: [300, 3886, 1332, 762]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage that answers the question.</instruction>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="agent">
        <instruction>Identify the specific value or calculation needed to answer the question based on the extracted data.</instruction>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="agent">
        <instruction>Perform the required mathematical operation or logical deduction using the identified value.</instruction>
        <depends_on>3</depends_on>
    </node>
    <node id="5" type="agent">
        <instruction>Verify the correctness of the result by cross-checking with the passage context.</instruction>
        <depends_on>4</depends_on>
    </node>
    <node id="6" type="output">
        <depends_on>5</depends_on>
    </node>