# Workflow ID: drop_310_0
# Benchmark: drop
# Data Indices: [2245, 1684, 2155, 694, 3226]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Extract key numerical data from the passage relevant to the question.</instruction>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="agent">
        <instruction>Identify and isolate the specific information needed to answer the question step by step.</instruction>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="agent">
        <instruction>Perform necessary calculations or logical deductions based on the extracted data.</instruction>
        <depends_on>3</depends_on>
    </node>
    <node id="5" type="agent">
        <instruction>Verify that the derived answer matches the question's requirements exactly.</instruction>
        <depends_on>4</depends_on>
    </node>
    <node id="6" type="output">
        <data>final_answer</data>
        <depends_on>5</depends_on>
    </node>